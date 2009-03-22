#ifndef HXWINDOW_H
#define HXWINDOW_H

#include <QtGui/QWidget>

namespace Ui {
    class Form;
}

namespace Phonon {
    class MediaObject;
};

class HxWindow : public QWidget {
    Q_OBJECT
    Q_DISABLE_COPY(HxWindow)
public:
    explicit HxWindow(QWidget *parent = 0);
    virtual ~HxWindow();

protected:
    virtual void changeEvent(QEvent *e);

private:
    Ui::Form *form;
    Phonon::MediaObject *musicPlayer;
};

#endif // HXWINDOW_H
