from generate import generate
import os
import subprocess
import sys



if (not os.path.exists("build")):
	os.mkdir("build")
else:
	for r,_,fl in os.walk("build"):
		for f in fl:
			os.remove(os.path.join(r,f))
if ("--generate" in sys.argv):
	print("Generating SHA1 Checking Code...")
	generate()
tmp=os.getcwd()
os.chdir("build")
if ("--gpu" in sys.argv):
	if ("--release" in sys.argv):
		if (subprocess.run(["nvcc","-O3","-Xptxas","-v,-O3","-use_fast_math","-D","_NVCC","-D","NDEBUG","-D","_WINDOWS","-D","_UNICODE","-D","UNICODE","-o","gpu_cracker.exe","../src/gpu_cracker/gpu_cracker.cu","-I","../src/gpu_cracker/include"]).returncode!=0):
			os.chdir(tmp)
			sys.exit(1)
	else:
		if (subprocess.run(["nvcc","-G","-use_fast_math","-D","_NVCC","-D","_DEBUG","-D","_WINDOWS","-D","_UNICODE","-D","UNICODE","-o","gpu_cracker.exe","../src/gpu_cracker/gpu_cracker.cu","-I","../src/gpu_cracker/include"]).returncode!=0):
			os.chdir(tmp)
			sys.exit(1)
	os.chdir(tmp)
	if ("--run" in sys.argv):
		subprocess.run(["build/gpu_cracker.exe"])
else:
	if ("--release" in sys.argv):
		if (subprocess.run(["cl","/c","/permissive-","/GS","/utf-8","/W3","/Zc:wchar_t","/Gm-","/sdl","/Zc:inline","/fp:precise","/D","NDEBUG","/D","_WINDOWS","/D","_UNICODE","/D","UNICODE","/errorReport:none","/WX","/Zc:forScope","/Gd","/Oi","/FC","/EHsc","/nologo","/diagnostics:column","/GL","/Gy","/Zi","/O2","/Oi","/MT","../src/cpu_cracker/*.c","/I","../src/cpu_cracker/include/"]).returncode!=0 or subprocess.run(["link","*.obj","/OUT:cpu_cracker.exe","/DYNAMICBASE","kernel32.lib","user32.lib","gdi32.lib","winspool.lib","comdlg32.lib","advapi32.lib","shell32.lib","ole32.lib","oleaut32.lib","uuid.lib","odbc32.lib","odbccp32.lib","/MACHINE:X64","/SUBSYSTEM:CONSOLE","/ERRORREPORT:none","/NOLOGO","/TLBID:1","/WX","/LTCG","/OPT:REF","/INCREMENTAL:NO","/OPT:ICF"]).returncode!=0):
			os.chdir(tmp)
			sys.exit(1)
	else:
		if (subprocess.run(["cl","/c","/permissive-","/GS","/utf-8","/W3","/Zc:wchar_t","/Gm-","/sdl","/Zc:inline","/fp:precise","/D","_DEBUG","/D","_WINDOWS","/D","_UNICODE","/D","UNICODE","/errorReport:none","/WX","/Zc:forScope","/Gd","/Oi","/FC","/EHsc","/nologo","/diagnostics:column","/ZI","/Od","/RTC1","/MTd","../src/cpu_cracker/*.c","/I","../src/cpu_cracker/include/"]).returncode!=0 or subprocess.run(["link","*.obj","/OUT:cpu_cracker.exe","/DYNAMICBASE","kernel32.lib","user32.lib","gdi32.lib","winspool.lib","comdlg32.lib","advapi32.lib","shell32.lib","ole32.lib","oleaut32.lib","uuid.lib","odbc32.lib","odbccp32.lib","/MACHINE:X64","/SUBSYSTEM:CONSOLE","/ERRORREPORT:none","/NOLOGO","/TLBID:1","/WX","/DEBUG","/INCREMENTAL"]).returncode!=0):
			os.chdir(tmp)
			sys.exit(1)
	os.chdir(tmp)
	if ("--run" in sys.argv):
		subprocess.run(["build/cpu_cracker.exe"])
