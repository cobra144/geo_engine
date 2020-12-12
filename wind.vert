#version 440

layout(location = 0) in vec4 position;
layout(location = 1) in vec4 color;



out vec3 interpColor;
//smooth out vec3 interpPosition;



uniform	mat4 cameraToClipMatrix;
uniform	mat4 worldToCameraMatrix;
uniform mat4 modelToWorldMatrix;

void main()
{
	vec4 temp = modelToWorldMatrix * position;
	//interpPosition = temp.xyz;
	temp = worldToCameraMatrix * temp;
	gl_Position = cameraToClipMatrix * temp;
	interpColor = color.xyz;
}
