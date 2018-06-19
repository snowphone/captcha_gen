#pragma once
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>	// C++

#include "yolo_v2_class.hpp"


std::vector<std::string> objects_names_from_file(std::string const filename);
void show_result(std::vector<bbox_t> const result_vec, std::vector<std::string> const obj_names);
void draw_boxes(cv::Mat mat_img, std::vector<bbox_t>& result_vec, const std::vector<std::string>& obj_names);

cv::Mat load_Mat(const std::string& image_filename);

cv::Mat image_t_to_mat(const image_t& img);

struct Data {
	int classes;
	std::string train,
		valid,
		names,
		backup;
};

Data read_data(const char* data_filename);
std::vector<std::string> get_image_list(const char* image_folder);
std::string get_new_name(const std::string& image_name, const std::string& epilogue = "results");
std::vector<std::string> read_image_name(const char* image_list);
std::string get_epoch(const std::string& weight_filename);
