{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages.default = pkgs.callPackage ./nix/pleck-jp.nix {
          fontforge-head = pkgs.callPackage ./nix/fontforge-head.nix { };
        };
        devShells.default = pkgs.mkShellNoCC {
          packages = with pkgs; [
            nil
          ];
        };
        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}
