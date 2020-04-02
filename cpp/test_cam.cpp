#include <opencv2/opencv.hpp>
#include <raspicam_cv.h>
#include <iostream>
#include <chrono>
#include <ctime>

using namespace std;
using namespace cv;
using namespace raspicam;

Mat frame, Matrix, framePers, frameGray, frameHSV, frameThresh, frameEdge;
RaspiCam_Cv Camera;
Point2f Source[] = {Point2f(140, 300), Point2f(580, 300), Point2f(50, 405), Point2f(670, 405)};
Point2f Destination[] = {Point2f(160, 200), Point2f(560, 200), Point2f(160, 405), Point2f(560, 405)};


void Setup(int argc, char **argv, RaspiCam_Cv &Camera)
{
    Camera.set(CAP_PROP_FRAME_WIDTH, ( "-w", argc, argv, 500 ));
    Camera.set(CAP_PROP_FRAME_HEIGHT, ( "-h", argc, argv, 320 ));
    Camera.set(CAP_PROP_BRIGHTNESS, ( "-br", argc, argv, 50 ));
    Camera.set(CAP_PROP_CONTRAST, ( "-co", argc, argv, 50 ));
    Camera.set(CAP_PROP_SATURATION, ( "-sa", argc, argv, 50 ));
    Camera.set(CAP_PROP_GAIN, ( "-g", argc, argv, 50 ));
    Camera.set(CAP_PROP_FPS, ( "-fps", argc, argv, 0 ));
}


void Capture() {
    Camera.grab();
    Camera.retrieve(frame);
    //cvtColor(frame, frame1, COLOR_BGR2RGB);
}

void Perspective()
{
    //~ line(frame, Destination[0], Destination[1], Scalar(0, 255, 0), 2);
    //~ line(frame, Destination[1], Destination[3], Scalar(0, 255, 0), 2);
    //~ line(frame, Destination[3], Destination[2], Scalar(0, 255, 0), 2);
    //~ line(frame, Destination[2], Destination[0], Scalar(0, 255, 0), 2);

    Matrix = getPerspectiveTransform(Source, Destination);
    warpPerspective(frame, framePers, Matrix, Size(500, 320));

    line(frame, Source[0], Source[1], Scalar(0, 0, 255), 2);
    line(frame, Source[1], Source[3], Scalar(0, 0, 255), 2);
    line(frame, Source[3], Source[2], Scalar(0, 0, 255), 2);
    line(frame, Source[2], Source[0], Scalar(0, 0, 255), 2);
}

void Threshold()
{
    cvtColor(framePers, frameGray, COLOR_RGB2GRAY);
    cvtColor(framePers, frameHSV, COLOR_BGR2HSV);
    inRange(frameGray, 50, 140, frameThresh);
    Canny(frameGray, frameEdge, 16, 50, 3, false);
}


int main(int argc, char **argv)
{
    Setup(argc, argv, Camera);
    cout<<"Connection to Camera"<<endl;
    if (!Camera.open())
    {
        cout<<"Failed to connect"<<endl;
        return -1;
    }
    cout<<"Camera ID: "<<Camera.getId()<<endl;

    while(1)
    {
        auto start = std::chrono::system_clock::now();
        Capture();
        Perspective();
        Threshold();
        auto end = std::chrono::system_clock::now();

        namedWindow("Original", WINDOW_KEEPRATIO);
        moveWindow("Original", 50, 100);
        resizeWindow("Original", 500, 405);
        imshow("Original", frameGray);
        waitKey(1);

        namedWindow("Gray", WINDOW_KEEPRATIO);
        moveWindow("Gray", 780, 100);
        resizeWindow("Gray", 500, 405);
        imshow("Gray", frameThresh);
        waitKey(1);

        namedWindow("Edge", WINDOW_KEEPRATIO);
        moveWindow("Edge", 50, 515);
        resizeWindow("Edge", 500, 405);
        imshow("Edge", frameEdge);
        waitKey(1);

        std::chrono::duration<double> elapsed_seconds = end - start;
        float t = elapsed_seconds.count();
        int FPS = 1/t;
        cout<<"FPS = "<<FPS<<endl;
    }

    return 0;
}
