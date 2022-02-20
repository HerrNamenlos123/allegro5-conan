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

    # Fixed dependencies
    requires = "libpng/1.6.37", "zlib/1.2.11", "libjpeg/9d", "libwebp/1.2.2", "freetype/2.11.1", "bzip2/1.0.8"

    def requirements(self):       # Conditional dependencies
        if self.settings.os != "Windows":
            self.requires("xorg/system")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        self.run("git clone git@github.com:HerrNamenlos123/allegro5-1.git --depth=1 --single-branch --branch=fix-cmake allegro5")
        #self.run("git clone https://github.com/liballeg/allegro5.git --depth=1 --single-branch --branch=5.2.7")

    def generate(self):

        zlib = self.dependencies["zlib"]
        libpng = self.dependencies["libpng"]
        libjpeg = self.dependencies["libjpeg"]
        libwebp = self.dependencies["libwebp"]
        freetype = self.dependencies["freetype"]
        bzip2 = self.dependencies["bzip2"]

        # Read paths into variables because they are read-only
        zlib_package_folder = zlib.package_folder
        libpng_package_folder = libpng.package_folder
        libjpeg_package_folder = libjpeg.package_folder
        libwebp_package_folder = libwebp.package_folder
        freetype_package_folder = freetype.package_folder
        bzip2_package_folder = bzip2.package_folder

        # Library paths cannot contain windows backspaces because of cmake's target_link_libraries()
        if self.settings.os == "Windows":
            zlib_package_folder = zlib_package_folder.replace("\\","/")
            libpng_package_folder = libpng_package_folder.replace("\\","/")
            libjpeg_package_folder = libjpeg_package_folder.replace("\\","/")
            libwebp_package_folder = libwebp_package_folder.replace("\\","/")
            freetype_package_folder = freetype_package_folder.replace("\\","/")
            bzip2_package_folder = bzip2_package_folder.replace("\\","/")

        # Configure dependency flags for cmake
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
        
        if self.settings.os == "Windows":
            flags += " -DWANT_STATIC_RUNTIME=" + str(self.settings.compiler.runtime == "MT").lower()
        else:
            flags += " -DWANT_STATIC_RUNTIME=false"

        flags += " -DPNG_PNG_INCLUDE_DIR=" + libpng_package_folder + "/include/"
        flags += " -DPNG_LIBRARY=" + libpng_package_folder + "/lib/libpng16.lib;"
        flags += " -DPNG_LIBRARIES=" + libpng_package_folder + "/lib/libpng16.lib;"
        flags += " -DPNG_FOUND=TRUE"

        flags += " -DJPEG_INCLUDE_DIR=" + libjpeg_package_folder + "/include/"
        flags += " -DJPEG_LIBRARY=" + libjpeg_package_folder + "/lib/libjpeg.lib;"
        flags += " -DJPEG_FOUND=TRUE"

        flags += " -DZLIB_INCLUDE_DIR=" + zlib_package_folder + "/include/"
        flags += " -DZLIB_LIBRARIES=" + zlib_package_folder + "/lib/zlib.lib"
        flags += " -DZLIB_FOUND=TRUE"

        flags += " -DWEBP_INCLUDE_DIRS=" + libwebp_package_folder + "/include/"
        flags += " -DWEBP_LIBRARIES=" + libwebp_package_folder + "/lib/webp.lib;" + \
            libwebp_package_folder + "/lib/webpdecoder.lib;" + \
            libwebp_package_folder + "/lib/webpdemux.lib;" + \
            libwebp_package_folder + "/lib/webpmux.lib"
        
        flags += " -DFREETYPE_INCLUDE_DIRS=" + freetype_package_folder + "/include/"
        flags += " -DFREETYPE_LIBRARY=" + freetype_package_folder + "/lib/freetype.lib;"
        flags += " -DBZIP2_INCLUDE_DIR=" + bzip2_package_folder + "/include/"
        flags += " -DBZIP2_LIBRARIES=" + bzip2_package_folder + "/lib/bz2.lib;"
        flags += " -DBZIP2_FOUND=TRUE"

        flags += " -DFREETYPE_PNG=on"
        flags += " -DFREETYPE_BZIP2=on"
        flags += " -DFREETYPE_ZLIB=on"

        # Call cmake generate
        if not os.path.exists("allegro5/build"):
            os.mkdir("allegro5/build")
        os.chdir("allegro5/build")
        self.run("cmake .. " + flags)

    def build(self):
        self.run("cd allegro5/build & cmake --build . --config RelWithDebInfo") # Build the project

    def package(self):
        self.copy("*", dst="include", src="allegro5/include")
        self.copy("*.lib", dst="lib", src="allegro5/build/lib/RelWithDebInfo")

    def package_info(self):
        self.cpp_info.libs = ["allegro_monolith-static"]

