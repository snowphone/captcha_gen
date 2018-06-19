#include <cassert>
#include <iostream>
#include <algorithm>
#include <memory>
#include <iterator>
#include <vector>
#include <string>
#include <numeric>


#include "misc.h"
#include "parser.h"
#include "yolo_v2_class.hpp"

using namespace std;

class Solver{
public:
	Solver(const char* data_path, const char* cfg_path, const char* weight_path, bool visible=false)
		: show_image(visible), detector(Detector(cfg_path, weight_path)) {
			data_record = read_data(data_path);
			obj_names = objects_names_from_file(data_record.names);
		}
	string predict(const string& image_name);
	double score(string label, string prediction);
	void flatten_boxes(const string& image_name, const string& epilogue, vector<bbox_t>& b_boxes);
	string get_label(string image_name);
	
private:
	void non_max_suppression(vector<bbox_t>& b_boxes);
	size_t get_square(int ux, int uy, int dx, int dy);
	float get_iou(bbox_t lhs, bbox_t rhs);

	Detector detector;
	std::vector<std::string> obj_names;
	bool show_image = false;
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
	cout << show_image << endl;
	cout << "Accuracy: " << accumulate(score_vector.begin(), score_vector.end(), 0.) / score_vector.size() << endl;
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
	if(lhs.x > rhs.x)
		swap(lhs, rhs);

	int common_area = get_square(rhs.x, rhs.y, lhs.x + lhs.h, lhs.y + lhs.w);
	int lhs_area = get_square(lhs.x, lhs.y, lhs.x + lhs.h, lhs.y + lhs.w),
		rhs_area = get_square(rhs.x, rhs.y, rhs.x + rhs.h, rhs.y + rhs.w);
	return (double)common_area / lhs_area + rhs_area - common_area;
}

void Solver::non_max_suppression(vector<bbox_t>& b_boxes)
{
	double thresh = 0.5;

	sort(b_boxes.begin(), b_boxes.end(), [](const bbox_t& lhs, const bbox_t& rhs){
			return lhs.prob > rhs.prob; });

	for(auto pivot = b_boxes.begin(); pivot != b_boxes.end(); ++pivot)
	{
		auto it = remove_if(pivot + 1, b_boxes.end(), [this, pivot, thresh](const bbox_t& i){return this->get_iou(*pivot, i) > thresh; });
		b_boxes.erase(it, b_boxes.end());
	}
}

// YOLO를 이용하여 Captcha를 해독하고, 그 string을 반환하는 함수
string Solver::predict(const string& image_name)
{
	image_t img = detector.load_image(image_name);
	vector<bbox_t> b_boxes = detector.detect_resized(img, img.w * 3, img.h * 3 );

	if(show_image)
		flatten_boxes(image_name , "_before_nms", b_boxes);

	non_max_suppression(b_boxes);

	if(show_image)
		flatten_boxes(image_name , "_after_nms", b_boxes);

	sort(b_boxes.begin(), b_boxes.end(), [](const bbox_t& lhs, const bbox_t& rhs){
			return lhs.x < rhs.x; });
	string ret;
	for_each(b_boxes.begin(), b_boxes.end(), [&ret, this](const bbox_t& i){ 
			string obj_name = this->obj_names[i.obj_id];
			ret.insert(ret.end(), obj_name.begin(), obj_name.end()); });
	return ret;
}

// bounding box를 image에 씌우는 함수
void Solver::flatten_boxes(const string& image_name, const string& epilogue, std::vector<bbox_t>& b_boxes)
{
	string folder = "./results/";
	cv::Mat image = load_Mat(image_name);
	draw_boxes(image, b_boxes, obj_names);
	string name = folder + get_new_name(image_name, epilogue);
	cout << name  << ",\t box: " << b_boxes.size() << endl;
	assert(cv::imwrite(name, image));
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


