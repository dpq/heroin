#include "hxgatekeeper.h"
#include <QTcpServer>
#include <QScriptValue>
#include <QScriptEngine>
#include <QSqlDatabase>
#include <QSqlQuery>

HxGateKeeper::HxGateKeeper(QObject *parent) : QTcpServer(parent) {
    games = new QHash<quint16, HxGameMaster*>();
    guests = new QList<QTcpSocket*>();
    jsEngine = new QScriptEngine();
    returnedPorts = new QList<quint16>();
    nextFreePort = HxGateKeeperStatic::GameMasterMinPort;
    connect(this, SIGNAL(newConnection()), this, SLOT(hello()));
    this->listen(QHostAddress::Any, HxGateKeeperStatic::GateKeeperPort);
}

HxGateKeeper::~HxGateKeeper() {
    qDeleteAll(*guests);
    qDeleteAll(*games);
    delete guests;
    delete games;
    delete jsEngine;
    delete returnedPorts;
}

void HxGateKeeper::hello() {
    QTcpSocket *guest = this->nextPendingConnection();
    this->guests->append(guest);
    guest->write(HxGateKeeperStatic::Hello.toUtf8());
    connect(guest, SIGNAL(readyRead()), this, SLOT(talk()));
}

void HxGateKeeper::talk() {
    QTcpSocket *guest = qobject_cast<QTcpSocket*>(sender());
    QList<QByteArray> request = guest->readAll().split('\n');
    if (request[0] == HxGateKeeperStatic::GameListRequest)
	sendGameList(guest);
    else if (request[0] == HxGateKeeperStatic::GameDetailsRequest) {
	sendGameDetails(guest, request[1].toInt());
    }
    else if (request[0] == HxGateKeeperStatic::GameReplayRequest)
	sendGameReplay(guest, request[1].toInt());
    else if (request[0] == HxGateKeeperStatic::GameCreateRequest) {
	if (returnedPorts->size() == 0 && nextFreePort < HxGateKeeperStatic::GameMasterMaxPort) {
	    quint16 port = nextFreePort++;
	    //createGame();
	}
	else if (returnedPorts->size() > 0) {
	    quint16 port = returnedPorts->takeFirst();
	    //createGame();
	}
	else
	    pardon(guest);
    }
    else if (request[0] == HxGateKeeperStatic::GameJoinRequest) {
	quint16 port = request[1].toInt();
	if (!games->contains(port))
	    pardon(guest);
	HxGameMaster *gm = games->value(request[1].toInt());
	//if (gm->state() == Open && gm->slotsAvailable() > 0) {
	//    farewell(guest);
//	}
//	else {
//	    pardon(guest);
//	}
    }
    else if (request[0] == HxGateKeeperStatic::GoodbyeRequest) {
	farewell(guest);
    }
    else {
	pardon(guest);
    }
}

void HxGateKeeper::farewell(QTcpSocket *guest) {
    guest->write(HxGateKeeperStatic::Begone.toUtf8());
    guest->close();
    disconnect(guest, SIGNAL(readyRead()), this, SLOT(talk()));
    guests->removeAll(guest);
    delete guest;
}

void HxGateKeeper::pardon(QTcpSocket *guest) {
    guest->write(HxGateKeeperStatic::Error.toUtf8());
}

void HxGateKeeper::createGame(const GameOptions &options) {

}

void HxGateKeeper::joinGame() {

}

void HxGateKeeper::sendGameList(QTcpSocket *guest) {
    foreach (HxGameMaster *gm, games->values()) {
	GameBasicInfo info = gm->basicInfo(guest->peerAddress());
	QString res = "{ ";
//	res += QString("gamePort: %1, ").arg(info.gamePort);
	res += QString("mapName: %2, ").arg(info.mapName);
	res += QString("isProtected: %3, ").arg(info.isProtected);
	res += QString("isAvailable: %4, ").arg(info.isAvailable);
	res += QString("difficultyLevel: %5, ").arg(info.difficultyLevel);
	res += QString("languageId: %6, ").arg(info.languageId);
	res += QString(", ").arg(info.totalSlots);
	res += QString(" }").arg(info.availableSlots);
	guest->write(res.toUtf8());
    }

    quint32 gamePort;
    QString mapName;
    bool isProtected;
    bool isAvailable;
    quint8 languageId;
    quint8 difficultyLevel;
    quint8 totalSlots;
    quint8 availableSlots;
}

void HxGateKeeper::sendGameDetails(QTcpSocket *guest, quint32 gameId) {
    GameDetailedInfo info = games->value(gameId)->detailedInfo();
    guest->write("");
}

void HxGateKeeper::sendGameReplay(QTcpSocket *guest, quint32 gameId) {
    QSqlDatabase db = QSqlDatabase::addDatabase("QMYSQL");
    db.setHostName("localhost");
    db.setDatabaseName("heroin");
    db.setUserName("heroin");
    db.setPassword("mumunibubua");
    bool ok = db.open();
    if (!ok) {
	// TODO return error
    }
    db.exec(QString("select body from replay where gameId==%1").arg(gameId));
    guest->write("");
    /* Try to connect to MySQL and download the replay
   Return an error and its description if failed (mysql not found, query error, empty set  */
}
