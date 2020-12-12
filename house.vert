#version 440

layout(location = 0) in vec4 position;
layout(location = 1) in vec4 normal;
layout(location = 2) in vec2 texCoord;



smooth out vec3 interpNormal;
smooth out vec3 interpPosition;
smooth out vec2 interpTexCoord;


uniform	mat4 cameraToClipMatrix;
uniform	mat4 worldToCameraMatrix;
uniform mat4 modelToWorldMatrix;


void main()
{
	vec4 temp = modelToWorldMatrix * position;
	interpPosition = temp.xyz;
	vec4 worldNormal = normalize(inverse(transpose(modelToWorldMatrix))*normal);
	//vec4 worldLightDir = normalize(worldLightPos - temp);
	temp = worldToCameraMatrix * temp;
	gl_Position = cameraToClipMatrix * temp;

	interpNormal = worldNormal.xyz;
    interpTexCoord = texCoord;
}
