{
  lib,
  stdenv,

  fontforge-head,
  python312,
  python312Packages,
}:
stdenv.mkDerivation {
  pname = "PleckJP";
  version = "1.3.0";

  src = lib.cleanSource ./..;

  nativeBuildInputs = [
    fontforge-head
    python312
    python312Packages.numpy
    python312Packages.fonttools
  ];

  installPhase = ''
    mkdir -p $out/share/fonts/truetype/PleckJP
    find ./build -name build/\*.ttf -exec mv {} $out/share/fonts/truetype/PleckJP \;
  '';

  meta = {
    description = "Programming Fonts (Hack + IBM Plex Sans JP + Nerd Fonts)";
    homepage = "https://github.com/ryota2357/PleckJP";
    license = with lib.licenses; [
      ofl
      bitstreamVera
      mit
    ];
  };
}
