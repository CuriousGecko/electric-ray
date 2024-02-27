# Maintainer: Leonid Tsybulsky <axonyx mail dot ru>

pkgname=lenovo-legion-electric-ray-git
pkgver=1.0
pkgrel=1
pkgdesc="Lenovo Legion 'Rapid charge' & 'Conservation'."
arch=('x86_64')
url="https://github.com/CuriousGecko/electric-ray"
license=('GPL')
depends=('python' 'pyside6' 'acpi')
source=(main.py constants.py images.py ui_main.py electric-ray)

package() {
    install -d "$pkgdir/usr/share/$pkgname/images"
    install main.py "$pkgdir/usr/share/$pkgname"
    install constants.py "$pkgdir/usr/share/$pkgname"
    install images.py "$pkgdir/usr/share/$pkgname"
    install ui_main.py "$pkgdir/usr/share/$pkgname"
    install -Dm755 electric-ray "$pkgdir/usr/bin/electric-ray"
    cp -r images/* "$pkgdir/usr/share/${pkgname}/images"
}

sha256sums=('814a6dc91f3d2934e4632ed03bd9a55c7ee7e5dc31e1a0a91c2f63418c93766c'
            '493386222e5fa4a78aa4317223bcf247fe6da79955e952278a46162350975311'
            '7053293bc390e3dcdca62e4d5299bc90abfcb425fa3d1c680a789bfc48649d7d'
            '1ab04dcd969731499918f8fa64bf4cce2f57b679346326609e9eb6fc000bac24'
            '97ebcf8eb6c66e1c03b97370458e8a714b1d3a52a7d245e08235e3be527ecf44')
