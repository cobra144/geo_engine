#version 440

//smooth in vec3 interpColor;
smooth in vec3 interpNormal;
smooth in vec3 interpPosition;
smooth in vec2 interpTexCoord;

uniform vec4 worldLightPos;
uniform vec4 spotLightDir;
uniform float spotLightAngle;
uniform vec4 worldCamPos;
uniform sampler2D tex0;
uniform sampler2D tex1;
uniform sampler2D tex2;



//uniform float4x4 gl_ModelViewProjectionMatrix;


uniform vec3 LightPos;
uniform vec3 CameraPos;     // The camera's current position
uniform vec3 LightDir;      // Direction vector to the light source
uniform vec3 InvWavelength; // 1 / pow(wavelength, 4) for RGB
uniform float CameraHeight;    // The camera's current height
uniform float CameraHeight2;   // fCameraHeight^2
uniform float OuterRadius;     // The outer (atmosphere) radius
uniform float OuterRadius2;    // fOuterRadius^2
uniform float InnerRadius;     // The inner (planetary) radius
uniform float InnerRadius2;    // fInnerRadius^2
uniform float KrESun;          // Kr * ESun
uniform float KmESun;          // Km * ESun
uniform float Kr4PI;           // Kr * 4 * PI
uniform float Km4PI;          // Km * 4 * PI
uniform float Scale;          // 1 / (fOuterRadius - fInnerRadius)
uniform float ScaleOverScaleDepth; // fScale / fScaleDepth
uniform float ScaleDepth;
uniform float Samples;
uniform int nSamples;
const float g = -0.95;
const float g2 = g*g;

out vec4 outputColor;

float scale(float fCos) {
    float x = 1.0 - fCos;
    return ScaleDepth * exp(-0.00287 + x*(0.459 + x*(3.83 + x*(-6.80 + x*5.25))));
}

float getNearIntersection(vec3 interpPosition, vec3 ray, float distance2, float radius2) {
    float B = 2.0 * dot(interpPosition, ray);
    float C = distance2 - radius2;
    float det = max(0.0, B*B - 4.0 * C);
    return 0.5 * (-B - sqrt(det));
}

void main()
{

	vec3 normal = normalize(interpNormal);
	vec3 worldLightDir = normalize(worldLightPos.xyz - interpPosition);
	vec3 worldCamDir = normalize(worldCamPos.xyz - interpPosition);
	vec3 refl =  reflect(-worldLightDir, normal);
	//vec3 refl = 2.0*normal*dot(normal,worldLightDir)-worldLightDir;//jw. tylko jawnie

	float dotLN  = max(0,dot(worldLightDir,normalize(interpNormal)));

	float dotRV  = pow(max(0,dot(worldCamDir,refl)),10.0);

	vec3 diffuseColor=vec3(0.0,1.0,1.0);
	vec3 specularColor=vec3(1.0,1.0,1.0);

	float d=0.5;
	float s=0.5;

	float dotLSL = max(0,dot(worldLightDir,normalize(spotLightDir.xyz)));

    vec4 texel = texture(tex2, interpTexCoord);
    //vec4 texel = vec4(1.0,1.0,1.0,1.0);

    //vec4 bump = texture(tex1, interpTexCoord);
    vec4 bump = vec4(1.0,1.0,1.0,1.0);
    vec3 Ray = interpPosition - CameraPos;
    float Far = length(Ray);
    Ray /= Far;

    float StartOffset;
    vec3 Start;

    if (length(CameraPos) > OuterRadius) {
        float Near = getNearIntersection(CameraPos, Ray, CameraHeight2, OuterRadius2);
        Start = CameraPos + Ray * Near;
        Far -= Near;
        float StartAngle = dot(Ray, Start) / OuterRadius;
        float StartDepth = exp(-1.0 / ScaleDepth);
        StartOffset = StartDepth * scale(StartAngle);
    } else {
        Start = CameraPos;
        float Height = length(Start);
        float Depth = exp(ScaleOverScaleDepth * (InnerRadius - CameraHeight));
        float StartAngle = dot(Ray, Start) / Height;
        StartOffset = Depth*scale(StartAngle);
    }

    // Initialize the scattering loop variables
    float SampleLength = Far / Samples;
    float ScaledLength = SampleLength * Scale;
    vec3 SampleRay = Ray * SampleLength;
    vec3 SamplePoint = Start + SampleRay * 0.5;


    // Now loop through the sample rays
    vec3 FrontColor = vec3(0.0, 0.0, 0.0);
    for(int i=0; i<nSamples; i++) {
        float Height = length(SamplePoint);
        float Depth = exp(ScaleOverScaleDepth * (InnerRadius - Height));
        float LightAngle = dot(LightPos, SamplePoint) / Height;
        float CameraAngle = dot(Ray, SamplePoint) / Height;
        float Scatter = (StartOffset + Depth*(scale(LightAngle) - scale(CameraAngle)));
        vec3 Attenuate = exp(-Scatter * (InvWavelength * Kr4PI + Km4PI));
        FrontColor += Attenuate * (Depth * ScaledLength);
        SamplePoint += SampleRay;
    }

    // Finally, scale the Mie and Rayleigh colors and set up the varying variables for the pixel shader
    vec4 secondaryColor = vec4(FrontColor * KmESun, 1.0);
    vec4 primaryColor = vec4(FrontColor * (InvWavelength * KrESun), 1.0);
    vec3 Direction = CameraPos - interpPosition;

    float Cos = dot(LightPos, Direction) / length(Direction);
    float RayleighPhase = 0.75 * (1.0 + Cos*Cos);
    float MiePhase = 1.5 * ((1.0 - g2) / (2.0 + g2)) * (1.0 + Cos*Cos) / pow(1.0 + g2 - 2.0*g*Cos, 1.5);
    outputColor = RayleighPhase * primaryColor + MiePhase * secondaryColor;
	if (dotLSL > cos(spotLightAngle))
		outputColor = (vec4(d*diffuseColor*dotLN,1.0)+vec4(s*specularColor*dotRV,1.0))*dotLSL;
	else
		outputColor = vec4(s*vec3(0.0,0.0,0.0)*dotRV,1.0) + vec4(d*vec3(0.0,0.0,0.0)*dotLN,1.0);
    outputColor = texel;
}
