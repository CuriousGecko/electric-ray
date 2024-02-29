# Maintainer: Leonid Tsybulsky <axonyx mail dot ru>

pkgname="electric-ray"
pkgver=1.0.1
pkgrel=1
pkgdesc="Lenovo Legion 'Rapid charge' & 'Conservation'."
arch=("x86_64")
url="https://github.com/CuriousGecko/electric-ray"
license=("GPL")
depends=("python" "pyside6" "acpi")
conflicts=("lenovo-legion-electric-ray-git")
source=("main.py" "constants.py" "images.py" "ui_main.py"
        "electric-ray" "README.md" "electric-ray.desktop")

package() {
    install -dm644 "$HOME/.config/electric-ray"
    install -Dm644 main.py "$pkgdir/usr/share/$pkgname/main.py"
    install -Dm644 constants.py "$pkgdir/usr/share/$pkgname/constants.py"
    install -Dm644 images.py "$pkgdir/usr/share/$pkgname/images.py"
    install -Dm644 ui_main.py "$pkgdir/usr/share/$pkgname/ui_main.py"
    install -Dm755 "$pkgname" "$pkgdir/usr/bin/electric-ray"
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
    install -Dm644 "$pkgname.desktop" "$pkgdir/usr/share/applications/$pkgname.desktop"
    install -Dm644 "$srcdir/images/icons/electric_ray_warning.png" \
                   "$pkgdir/usr/share/$pkgname/images/icons/electric_ray_warning.png"
    install -Dm644 "$srcdir/images/icons/electric_ray.png" \
                   "$pkgdir/usr/share/$pkgname/images/icons/electric_ray.png"
}

sha256sums=('814a6dc91f3d2934e4632ed03bd9a55c7ee7e5dc31e1a0a91c2f63418c93766c'
            '8bb32fa900cb17d512ea47dc3c422b569412a1159f629caf81a2512545fd7e1e'
            '7053293bc390e3dcdca62e4d5299bc90abfcb425fa3d1c680a789bfc48649d7d'
            '1ab04dcd969731499918f8fa64bf4cce2f57b679346326609e9eb6fc000bac24'
            '5241270b160a05c9c988b3d0ad7a85829d51c6a20f5cc2d44e3e6f793869fd0f'
            'b9e389df15a752d95d30184e7dbab4d3dad882694966459989dfe4c0c0dd2a70'
            'bf4b7bcbf105f4b7d131a24c9a8471e49a239e3e4f8634f4fb42e33ce5ad95b4')
