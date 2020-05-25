
# How to contribute

## Initialization

* Fork this repo
* Clone to your machine

      git clone --recursive <URL>

* Install hugo:

      cd /tmp
      wget https://github.com/gohugoio/hugo/releases/download/v0.57.2/hugo_0.57.2_Linux-64bit.deb
      sudo dpkg -i hugo*.deb

## Make updates

### To preview updates

      cd hugo
      hugo server -D

### To update content

* check scripts ``data2hugo``
* make updates
* preview updates with `make hugo` command
* send pull request to this repo


### To update theme

* check folder ``hugo/themes/``
* copy files you want to modify to `hugo/` folder
* make updates
* preview updates
* make git commit
* send pull request to this repo

