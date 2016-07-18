
ANDROID_BASE=/usr/local/androidsdk
ANDROID_HOME=$ANDROID_BASE/android-sdk-linux

origin=$PWD

mkdir $ANDROID_BASE
cd $ANDROID_BASE
wget https://dl.google.com/android/android-sdk_r24.4.1-linux.tgz
unzip android-sdk_r24.4.1-linux.tgz

echo "# Android SDK" >> ~/.profile
echo "export ANDROID_HOME=""/usr/local/android-sdk/android-sdk-linux""" >> ~/.profile
echo "export ANDROID=\$ANDROID_HOME/tools" >> ~/.profile
echo "export PATH=\$ANDROID:\$PATH" >> ~/.profile

# install the newest version of the SDK tools
android update sdk --all

# needed for some compilation stuff to work
apt-get install lib32stdc++6 lib32z1