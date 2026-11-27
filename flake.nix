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
            (python314.withPackages (p: [
              p.brotli
              p.fontforge
              p.fonttools
              p.numpy
            ]))
            gnused
            nodejs
            zip
            coreutils
            curl
            nil
            pyright
          ];
        };
        formatter = treefmt-nix.lib.mkWrapper pkgs {
          projectRootFile = "flake.nix";
          programs = {
            black.enable = true;
            nixfmt.enable = true;
            yamlfmt = {
              enable = true;
              settings.formatter.retain_line_breaks = true;
            };
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
