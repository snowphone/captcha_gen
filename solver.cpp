#include <cassert>
#include <iostream>
#include <algorithm>
#include <memory>
#include <iterator>
#include <vector>
#include <string>
#include <numeric>


#define OPENCV
#include "misc.h"
#include "parser.h"
#include "yolo_v2_class.hpp"

using namespace std;

class Solver{
public:
	Solver(const char* data_path, const char* cfg_path, const char* weight_path, bool visible=false);
	string predict(const string& image_name);
	double score(string label, string prediction);
	void flatten_boxes(cv::Mat image, const string& image_name, const string& epilogue, vector<bbox_t>& b_boxes);
	string get_label(string image_name);
	void resize(cv::Mat& mat, double ratio);
	
private:
	size_t non_max_suppression(vector<bbox_t>& b_boxes);
	size_t get_square(int ux, int uy, int dx, int dy);
	float get_iou(bbox_t lhs, bbox_t rhs);

	Detector detector;
	std::vector<std::string> obj_names;
	bool show_image;
	Data data_record;
};

int main(int argc, const char* argv[])
{
	const char* image_list = find_option(argc, argv, "-image", nullptr);
	const char* weight_filename = find_option(argc, argv, "-weight", nullptr);
	const char* data_filename = find_option(argc, argv, "-data", nullptr);
	const char* cfg_filename = find_option(argc, argv, "-cfg", nullptr);
	bool show_image = (bool)find(argc, argv, "-show", nullptr);

	if (!image_list || !weight_filename || !data_filename || !cfg_filename)
	{
		throw runtime_error(string("Usage: ") + argv[0] + " -data <data> -cfg <cfg> -weight <weight> -image <image folder> [-show]");
	}

    vector<string> image_names = get_image_list(image_list);
	Solver solver(data_filename, cfg_filename, weight_filename, show_image);

	vector<double> score_vector;
    for(string image_name : image_names)
    {
		string label = solver.get_label(image_name),
			   prediction = solver.predict(image_name);
		double cur_score = solver.score(label, prediction);
		cout << label << '\t' << prediction << '\t' << cur_score << endl;
		score_vector.push_back(cur_score);
    }
	double accuracy = accumulate(score_vector.begin(), score_vector.end(), 0.) / score_vector.size();
	cout << "Accuracy: " << accuracy * 100 << "%"  << endl;
}


Solver::Solver(const char* data_path, const char* cfg_path, const char* weight_path, bool visible)
		: show_image(visible), detector(Detector(cfg_path, weight_path)) 
{
	data_record = read_data(data_path);
	obj_names = objects_names_from_file(data_record.names);
}

// regex: .*label_([0-9A-Z]+).jpg 를 추출
string Solver::get_label(string image_name)
{
	string beg = "label_", ext = image_name.substr(image_name.rfind('.'));
	string::size_type first = image_name.find(beg) + beg.size(), last = image_name.find(ext);
	return image_name.substr(first, last - first);
}

//leftupper x, leftupper y, rightlower x, rightlower y
size_t Solver::get_square(int ux, int uy, int dx, int dy)
{
	return abs(ux - dx) * abs(uy - dy);
}

float Solver::get_iou(bbox_t lhs, bbox_t rhs)
{
	cv::Rect box1(lhs.x, lhs.y, lhs.w, lhs.h),
		box2(rhs.x, rhs.y, rhs.w, rhs.h),
		intersection = box1 & box2;		//intersecion operator

	double intersection_area = intersection.width * intersection.height,
		union_area = (box1.width * box1.height) + (box2.width * box2.height) - intersection_area;

	return intersection_area / union_area;
}

size_t Solver::non_max_suppression(vector<bbox_t>& b_boxes)
{
	double thresh = 0.5;
	size_t removed_boxes=0;

	sort(b_boxes.begin(), b_boxes.end(), [](const bbox_t& lhs, const bbox_t& rhs){
			return lhs.prob > rhs.prob; });

	for(auto pivot = b_boxes.begin(); pivot != b_boxes.end(); ++pivot)
	{
		auto it = remove_if(pivot + 1, b_boxes.end(), [this, pivot, thresh](const bbox_t& i){
				return this->get_iou(*pivot, i) > thresh; });
		removed_boxes += distance(it, b_boxes.end());
		b_boxes.erase(it, b_boxes.end());
	}
	return removed_boxes;
}

// YOLO를 이용하여 Captcha를 해독하고, 그 string을 반환하는 함수
string Solver::predict(const string& image_name)
{
	cv::Mat img = cv::imread(image_name);
	resize(img, 3.);
	vector<bbox_t> b_boxes = detector.detect(img);


	non_max_suppression(b_boxes);

	if(show_image)
		flatten_boxes(img, image_name , "_after_nms", b_boxes);

	sort(b_boxes.begin(), b_boxes.end(), [](const bbox_t& lhs, const bbox_t& rhs){
			return lhs.x < rhs.x; });
	string ret;
	for_each(b_boxes.begin(), b_boxes.end(), [&ret, this](const bbox_t& i){ 
			string obj_name = this->obj_names[i.obj_id];
			ret.insert(ret.end(), obj_name.begin(), obj_name.end()); });
	return ret;
}

// bounding box를 image에 씌우는 함수
void Solver::flatten_boxes(cv::Mat image, const string& image_name, const string& epilogue, std::vector<bbox_t>& b_boxes)
{
	string folder = "./results/";
	draw_boxes(image, b_boxes, obj_names);
	string name = folder + get_new_name(image_name, epilogue);
	cout << name  << ",\t box: " << b_boxes.size() << endl;
	cv::imwrite(name, image);
}

// 정답과 예측값 사이에 몇 글자나 맞추었는지 계산.
// Longest Common Sequence, reward: 1, penalty: 0
double Solver::score(string label, string prediction)
{
	auto fn = [&label, &prediction] (auto f, string::iterator it, string::iterator jt) -> double
	{
		if(it == label.end() || jt == prediction.end())
			return 0.;
		if(*it == *jt)
			return 1. + f(f, it+1, jt+1);
		return max(f(f, it+1, jt), f(f, it, jt+1));
	};
	return fn(fn, label.begin(), prediction.begin()) / label.size();
}

void Solver::resize(cv::Mat& mat, double ratio)
{
	cv::resize(mat, mat, cv::Size(), ratio, ratio, CV_INTER_CUBIC);
}
