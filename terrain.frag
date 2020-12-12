#version 440

smooth in vec3 interpColor;
smooth in vec3 interpNormal;
smooth in vec3 interpPosition;
smooth in vec2 interpTexCoord;


uniform uint light;
uniform uint terrainHypso;

uniform vec4 worldLightPos;
uniform vec4 spotLightDir;
uniform float spotLightAngle;
uniform vec4 worldCamPos;
uniform sampler2D tex0;
uniform sampler2D tex1;
uniform sampler2D tex2;
uniform float lightForce;

uniform	mat4 cameraToClipMatrix;
uniform	mat4 worldToCameraMatrix;
uniform vec2 pos;


out vec4 outputColor;
out vec4 multipliedVector;

void main()
{

    mat4 ProjView = cameraToClipMatrix*worldToCameraMatrix;
    mat4 ProjViewInversed = inverse(ProjView);
    vec4 vector = vec4(pos[0], pos[1], 0.0, 1.0);
    vec4 multipliedVector = vector * ProjViewInversed;
	vec3 normal = normalize(interpNormal);
	vec3 worldLightDir = normalize(worldLightPos.xyz - interpPosition);
	vec3 worldCamDir = normalize(worldCamPos.xyz - interpPosition);
	vec3 refl =  reflect(-worldLightDir, normal);
	//vec3 refl = 2.0*normal*dot(normal,worldLightDir)-worldLightDir;//jw. tylko jawnie

	float dotLN  = max(0,dot(worldLightDir,normalize(interpNormal)));

	float dotRV  = pow(max(0,dot(worldCamDir,refl)),10.0);

	vec3 diffuseColor=vec3(1.0,1.0,1.0);
	vec3 specularColor=vec3(1.0,1.0,1.0);

	float d=0.5;
	float s=0.5;

	float dotLSL = max(0,dot(worldLightDir,normalize(spotLightDir.xyz)));

    vec4 texel = texture(tex0, interpTexCoord);
    //vec4 texel = vec4(1.0,1.0,1.0,1.0);

    //vec4 bump = texture(tex1, interpTexCoord);
    vec4 bump = vec4(1.0,1.0,1.0,1.0);

    if (light==1)
    {
        if (terrainHypso==0)
        {
            if (dotLSL > cos(spotLightAngle))
                outputColor = lightForce*((vec4(texel.zyz*d*diffuseColor*dotLN,1.0)+vec4(texel.xyz*s*specularColor*dotRV,1.0))*dotLSL);
            else
                outputColor =  lightForce*(vec4(s*vec3(0.0,0.0,0.0)*dotRV,1.0) + vec4(d*vec3(0.0,0.0,0.0)*dotLN,1.0));
        }
        else
        {
            if (dotLSL > cos(spotLightAngle))
                outputColor = lightForce*((vec4(interpColor*d*diffuseColor*dotLN,1.0)+vec4(interpColor*s*specularColor*dotRV,1.0))*dotLSL);
            else
                outputColor =  lightForce*(vec4(s*vec3(0.0,0.0,0.0)*dotRV,1.0) + vec4(d*vec3(0.0,0.0,0.0)*dotLN,1.0));
        }
    }
    else
    {
         if (terrainHypso==0)
            outputColor = texel;
         else
            outputColor = vec4(interpColor,1.0);
    }

}
