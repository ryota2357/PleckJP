{
  lib,
  stdenv,
  fetchFromGitHub,
  # gettext,
  cmake,
  ninja,
  # pkg-config,
  python,

  cairo,
  freetype,
  giflib,
  gtk3,
  libjpeg,
  pango,
  libpng,
  libspiro,
  libtiff,
  libxml2,
  woff2,

  # zlib,
  # glib,
  # readline,
  # zeromq,
  # Carbon,
  # Cocoa,
}:
stdenv.mkDerivation rec {
  pname = "fontforge";
  version = "9af60edefc61d1f9244601802067c33fd221db69";

  src = fetchFromGitHub {
    owner = pname;
    repo = pname;
    rev = version;
    sha256 = "";
  };

  nativeBuildInputs = [ cmake ninja ];
  buildInputs = [
    woff2 python freetype giflib libpng libjpeg libtiff libxml2
    libspiro gtk3 cairo pango
  ];

  buildPhase = ''
    mkdir build
    cd build
    ${lib.getExe cmake} -GNinja ..
    ${lib.getExe ninja}
    ${lib.getExe ninja} install
    ${lib.getExe ninja} clean
  '';
}
