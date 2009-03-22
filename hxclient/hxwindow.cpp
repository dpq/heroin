#include "hxwindow.h"
#include "ui_hxwindow.h"
#include <phonon/MediaObject>

HxWindow::HxWindow(QWidget *parent) : form(new Ui::Form) {
    form->setupUi(this);
    musicPlayer = Phonon::createPlayer(Phonon::MusicCategory, Phonon::MediaSource(":/mp3/main.mp3"));
    musicPlayer->play();
}

HxWindow::~HxWindow() {
    delete form;
    delete musicPlayer;
}

void HxWindow::changeEvent(QEvent *e) {
    switch (e->type()) {
    case QEvent::LanguageChange:
	form->retranslateUi(this);
        break;
    default:
        break;
    }
}
