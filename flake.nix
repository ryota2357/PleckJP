{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      treefmt-nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShellNoCC {
          packages = with pkgs; [
            (python313.withPackages (p: [
              p.fontforge
              p.fonttools
              p.numpy
            ]))
            gnused
            zip
            coreutils
            nil
            pyright
          ];
        };
        formatter = treefmt-nix.lib.mkWrapper pkgs {
          projectRootFile = "flake.nix";
          programs = {
            black.enable = true;
            nixfmt.enable = true;
            yamlfmt.enable = true;
          };
          settings.global.excludes = [
            ".envrc"
            "images/*"
            "build/*"
            "resources/*"
          ];
        };
      }
    );
}
