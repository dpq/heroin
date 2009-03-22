#include <QtGui/QApplication>
#include <QStackedWidget>
#include <QHBoxLayout>
#include "hxwindow.h"

int main(int argc, char *argv[]) {
    QApplication a(argc, argv);
    HxWindow w;
    w.showFullScreen();
    return a.exec();
}
