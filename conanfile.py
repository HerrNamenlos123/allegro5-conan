from conans import ConanFile, CMake, tools
import os

class Allegro5Conan(ConanFile):
    name = "allegro5"
    version = "5.2.7"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Allegro5 here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    # Dependencies
    requires = "libpng/1.6.37", "zlib/1.2.11", "libjpeg/9d", "libwebp/1.2.2", "freetype/2.11.1"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):

        # Check if the DirectX SDK is installed
        if self.settings.os == "Windows":
            if not os.path.exists(str(os.getenv("DXSDK_DIR"))):
                raise Exception("Please make sure the DirectX SDK is installed! Download from https://www.microsoft.com/en-us/download/details.aspx?id=6812")

        self.run("git clone https://github.com/liballeg/allegro5.git --depth=1 --single-branch --branch=5.2.7")

    def generate(self):

        zlib = self.dependencies["zlib"]
        libpng = self.dependencies["libpng"]
        libjpeg = self.dependencies["libjpeg"]
        libwebp = self.dependencies["libwebp"]
        freetype = self.dependencies["freetype"]

        flags = "-Wno-dev"
        flags += " -DPREFER_STATIC_DEPS=true"
        flags += " -DSHARED=" + str(self.options.shared).lower()
        flags += " -DWANT_DOCS=false"
        flags += " -DWANT_DOCS_HTML=false"
        flags += " -DWANT_EXAMPLES=false"
        flags += " -DWANT_FONT=true"
        flags += " -DWANT_MONOLITH=true"
        flags += " -DWANT_TESTS=false"
        flags += " -DWANT_DEMO=false"
        flags += " -DWANT_RELEASE_LOGGING=false"
        flags += " -DWANT_STATIC_RUNTIME=" + str(self.settings.compiler.runtime == "MT").lower()

        flags += " -DPNG_PNG_INCLUDE_DIR=" + libpng.package_folder + "/include/"
        flags += " -DPNG_LIBRARY=" + libpng.package_folder + "/lib/libpng16.lib"

        flags += " -DJPEG_INCLUDE_DIR=" + libjpeg.package_folder + "/include/"
        flags += " -DJPEG_LIBRARY=" + libjpeg.package_folder + "/lib/libjpeg.lib"

        flags += " -DZLIB_INCLUDE_DIR=" + zlib.package_folder + "/include/"

        flags += " -DWEBP_INCLUDE_DIRS=" + libwebp.package_folder + "/include/"
        flags += " -DWEBP_LIBRARIES=" + libwebp.package_folder + "/lib/webp.lib;" + \
            libwebp.package_folder + "/lib/webpdecoder.lib;" + \
            libwebp.package_folder + "/lib/webpdemux.lib;" + \
            libwebp.package_folder + "/lib/webpmux.lib"
        
        flags += " -DFREETYPE_INCLUDE_DIRS=" + freetype.package_folder + "/include/"
        flags += " -DFREETYPE_LIBRARY=" + freetype.package_folder + "/lib/freetype.lib"

        print(flags)
        self.run("cd allegro5 && mkdir build && cd build && cmake .. " + flags)

    def build(self):
        self.run("cd allegro5/build && cmake --build . --config RelWithDebInfo")

    def package(self):
        self.copy("*", dst="include", src="allegro5/include")
        self.copy("*.lib", dst="lib", src="allegro5/build/lib/RelWithDebInfo")

    def package_info(self):
        self.cpp_info.libs = ["allegro_monolith-static"]

