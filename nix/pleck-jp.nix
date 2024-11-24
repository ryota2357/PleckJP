{
  lib,
  stdenv,
}:
stdenv.mkDerivation {
  pname = "PleckJP";
  version = "1.3.0";
  meta = {
    description = "A CLI tool to quickly set up custom local playgrounds";
    homepage = "https://github.com/ryota2357/PleckJP";
    license = with lib.licenses; [
      ofl
      bitstreamVera
      mit
    ];
  };
}
