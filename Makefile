install:
  sudo apt-get update
  curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
  sudo apt-get install nodejs npm node-semver
  sudo apt-get install scons python-dev
  cd rpi_ws281x
  sudo scons
  cd python
  sudo python setup.py build
  sudo python setupt.py install
  cd ../../sharkled
  sudo pip install -r requirements.txt
