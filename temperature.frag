#version 440

smooth in vec3 interpColor;
smooth in vec3 interpPosition;


uniform vec4 worldCamPos;




out vec4 outputColor;

void main()
{



    outputColor = vec4(interpColor,1.0);
}
