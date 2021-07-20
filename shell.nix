{ pkgs ? import <nixpkgs> {} }:
with pkgs;
mkShell {
  buildInputs = [
    (python3.withPackages (p: [p.bleak p.pytest p.crcmod p.black]))
    imagemagick

    pkgs.bashInteractive
  ];
}
