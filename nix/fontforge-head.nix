{
  stdenv,
  fetchFromGitHub,

  cmake,
  ninja,
  pkg-config,

  cairo,
  freetype,
  giflib,
  gtk3,
  libjpeg,
  libpng,
  libspiro,
  libtiff,
  libxml2,
  pango,
  python312,
  readline,
  woff2,

  glib,
  zlib,
  zeromq,
  uthash,
}:
stdenv.mkDerivation rec {
  pname = "fontforge";
  version = "9af60edefc61d1f9244601802067c33fd221db69";

  src = fetchFromGitHub {
    owner = pname;
    repo = pname;
    rev = version;
    sha256 = "sha256-rhChvBhqOEWkDQ8nO6xgOS9YDn79jvRJLw4ICuedJa8=";
  };

  nativeBuildInputs = [
    pkg-config
    cmake
    ninja
  ];
  buildInputs = [
    ninja
    readline
    woff2
    python312
    freetype
    giflib
    libpng
    libjpeg
    libtiff
    libxml2
    libspiro
    gtk3
    cairo
    pango
    glib
    zlib
    zeromq
    uthash
  ];
  cmakeFlags = [
    "-DCMAKE_BUILD_WITH_INSTALL_RPATH=ON"
    "-DENABLE_FONTFORGE_EXTRAS=ON"
  ];

  # buildPhase = ''
  #   mkdir -p build
  #   cd build
  #   cmake -GNinja ${src}
  #   ninja
  # '';
  #
  # installPhase = ''
  #   mkdir -p $out
  #   ninja install
  # '';
}
