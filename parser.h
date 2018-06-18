#include <algorithm>
#include <cstring>
#include <string>


void erase(int& argc, const char** argv, int index);

const char* find(int& argc, const char** argv, const char* item, const char* default_str=nullptr);

const char* find_option(int& argc, const char** argv, const char* option, const char* default_str=nullptr);

