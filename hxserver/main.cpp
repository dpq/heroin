#include "hxgatekeeper.h"
#include <QCoreApplication>

/*
The Heroin server consists of two parts: the gatekeeper and the gamemaster.
The gatekeeper listens to a fixed port and allows clients
- to create new games (including private ones)
- to request the list of all games running on this server
- to join a game
Besides, the gatekeeper is responsible for launching and destroying gamemasters, each game being served by a separate process.
*/

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);
    HxGateKeeper gk(&app);
    return app.exec();
}
