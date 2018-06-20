#include <cassert>
#include <iostream>
#include <algorithm>
#include <memory>
#include <iterator>
#include <vector>
#include <string>
#include <numeric>
#include <fstream>


#define OPENCV
#include "misc.h"
#include "yolo_v2_class.hpp"

using namespace std;

void flatten_boxes(cv::Mat image, const string& image_name, const string& epilogue, std::vector<bbox_t>& b_boxes);
vector<vector<bbox_t>> get_bbox(vector<string> image_list);

int main(int argc, const char* argv[])
{

	if (argc < 2)
	{
		throw runtime_error(string("Usage: ") + argv[0] + " <image folder>");
	}

	vector<string> image_list = get_image_list(argv[1]);
	vector<vector<bbox_t>> bbox_list = get_bbox(image_list);

	for(int i=0; i < image_list.size(); ++i )
	{
		cv::Mat mat = cv::imread(image_list[i]);
		flatten_boxes(mat, image_list[i], "flatten", bbox_list[i]);
	}
}

vector<vector<bbox_t>> get_bbox(vector<string> image_list)
{
	vector<vector<bbox_t>> ret;
	for(string& image : image_list)
	{
		string::size_type index = image.rfind("jpg");
		if (index == string::npos)
			index = image.rfind("png");
		if (index == string::npos)
			throw runtime_error("unsupported image type. It supports only jpg, png file");

		cv::Mat mat = cv::imread(image);
		image.replace(image.begin() + index, image.end(), "txt");

		FILE* fp = fopen(image.c_str(), "r");
		int cls;
		float x, y, w, h;
		vector<bbox_t> box_list;
		while(~fscanf(fp, "%d %f %f %f %f", &cls, &x, &y, &w, &h))
		{
			bbox_t box;
			box.prob = 0;
			box.track_id = 0;
			box.obj_id = cls;
			box.w = w * mat.cols;
			box.h = h * mat.rows;
			box.x = x * mat.cols - 0.5 * box.w;
			box.y = y * mat.rows - 0.5 * box.h;
			box_list.push_back(box);
			cout << cls << " " << x << " " << y << " " << w << " " << h << endl;

		}
		ret.push_back(box_list);
		fclose(fp);
	}
	return ret;
}



// bounding box를 image에 씌우는 함수
void flatten_boxes(cv::Mat image, const string& image_name, const string& epilogue, std::vector<bbox_t>& b_boxes)
{
	string folder = "./results/";
	vector<string> obj_names;
	string alpha = "abcdefghijklmnopqrstuvwxyz";
	for(auto i : alpha)
	{
		obj_names.push_back(string(1, i));
	}
	draw_boxes(image, b_boxes, obj_names);
	string name = folder + get_new_name(image_name, epilogue);
	cout << name  << ",\t box: " << b_boxes.size() << endl;
	cv::imwrite(name, image);
}

