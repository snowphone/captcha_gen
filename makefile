TARGET= solver flatter
OBJECT =  misc.o parser.o 
darknet = ./darknet.so

#헤더파일
CXXFLAGS = -O2 -std=c++14 
CXX=clang++

LINK = -lopencv_videoio -lopencv_imgproc -lopencv_imgcodecs -lopencv_core

#확장자 규칙: 모든 cpp파일을 object 파일로 컴파일
.SUFFIXES : .o .cpp
%.o : %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

solver :  $(OBJECT) solver.o
	$(CXX) $(LINK) -o $@ $^  $(darknet)

flatter :  $(OBJECT) flatter.o
	$(CXX) $(LINK) -o $@ $^  $(darknet)

clean:
	$(RM) $(TARGET) *.o $(TARGET)

