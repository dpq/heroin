#include "hxgatekeeper.h"
#include <QTcpServer>
#include <QScriptValue>
#include <QScriptEngine>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QDataStream>

HxGateKeeper::HxGateKeeper(QObject *parent) : QTcpServer(parent) {
	games = new QHash<quint16, HxGameMaster*>();
	guests = new QList<QTcpSocket*>();
	jsEngine = new QScriptEngine();
	reclaimedPorts = new QList<quint16>();
	nextFreePort = HxGateKeeperStatic::GameMasterMinPort;
	nextGameId = 0; //TODO retrieve from the database
	connect(this, SIGNAL(newConnection()), this, SLOT(hello()));
	this->listen(QHostAddress::Any, HxGateKeeperStatic::GateKeeperPort);
}

HxGateKeeper::~HxGateKeeper() {
	qDeleteAll(*guests);
	qDeleteAll(*games);
	delete guests;
	delete games;
	delete jsEngine;
	delete reclaimedPorts;
}

void HxGateKeeper::hello() {
	QTcpSocket *guest = this->nextPendingConnection();
	this->guests->append(guest);
	guest->write(HxGateKeeperStatic::Hello.toUtf8());
	connect(guest, SIGNAL(readyRead()), this, SLOT(talk()));
	connect(guest, SIGNAL(disconnected()), this, SLOT(forget()));
}

void HxGateKeeper::talk() {
	QTcpSocket *guest = qobject_cast<QTcpSocket*>(sender());
	QList<QByteArray> request = guest->readAll().split('\n');
	if (request[0] == HxGateKeeperStatic::GameListRequest) {
		sendGameList(guest);
	}
	else if (request[0] == HxGateKeeperStatic::GameDetailsRequest) {
		sendGameDetails(guest, request[1].toInt());
	}
	else if (request[0] == HxGateKeeperStatic::GameReplayRequest) {
		sendGameReplay(guest, request[1].toInt());
	}
	else if (request[0] == HxGateKeeperStatic::GameCreateRequest) {
		if (reclaimedPorts->size() > 0 || nextFreePort < HxGateKeeperStatic::GameMasterMaxPort) {
			try {
				QDataStream in(guest);
				QString mapName;
				QString password;
				QPair<QHostAddress, quint16> subnetRestriction;
				qint32 pingRestriction;
				quint8 languageId;
				quint8 difficultyLevel;
				in >> mapName >> password >> subnetRestriction >> pingRestriction >> languageId >> difficultyLevel;
				GameOptions go;
				go.mapName = mapName;
				go.password = password;
				go.subnetRestriction = subnetRestriction;
				go.pingRestriction = pingRestriction;
				go.languageId = languageId;
				go.difficultyLevel = difficultyLevel;
				createGame(go);
			}
			catch(int e) {
				pardon(guest, QString("Game options object expected."));
			}
		}
		else {
			pardon(guest, QString("Server running at full capacity. Try again later."));
		}
	}
	else if (request[0] == HxGateKeeperStatic::GameJoinRequest) {
		quint16 port = request[1].toInt();
		if (!games->contains(port)) {
			pardon(guest, QString("No such game currently exists."));
		}
		HxGameMaster *gm = games->value(request[1].toInt());
		GameBasicInfo gi = gm->basicInfo(guest->peerAddress());
		if (gi.gameState == OpenState && gi.availableSlots > 0) {
			//TODO
		}
		else {
			pardon(guest, QString("You cannot join this game right now."));
		}
	}
	else if (request[0] == HxGateKeeperStatic::GoodbyeRequest) {
		farewell(guest);
	}
	else {
		pardon(guest, QString("Bad request."));
	}
}

void HxGateKeeper::farewell(QTcpSocket *guest) {
	guest->write(HxGateKeeperStatic::Begone.toUtf8());
	guest->close();
	// TODO Kick the player from all games he's in
	disconnect(guest, SIGNAL(readyRead()), this, SLOT(talk()));
	guests->removeAll(guest);
	guest->deleteLater();;
}

void HxGateKeeper::pardon(QTcpSocket *guest, QString message) {
	guest->write(HxGateKeeperStatic::Error.toUtf8());
	guest->write(message.toUtf8());
}

void HxGateKeeper::forget() {
	QTcpSocket *guest = qobject_cast<QTcpSocket*>(sender());
	disconnect(guest, SIGNAL(readyRead()), this, SLOT(talk()));
	guests->removeAll(guest);
	guest->deleteLater();
}

quint16 HxGateKeeper::createGame(const GameOptions &options) {
	quint16 port;
	if (reclaimedPorts->size() > 0) {
		port = reclaimedPorts->takeFirst();
	}
	else if (nextFreePort < HxGateKeeperStatic::GameMasterMaxPort) {
		port = nextFreePort++;
	}
	else {
		throw 1;
	}
	HxGameMaster *game = new HxGameMaster(nextGameId++, options);
	games->insert(port, game);
	return port;
}

void HxGateKeeper::joinGame(quint16 port) {

}

void HxGateKeeper::sendGameList(QTcpSocket *guest) {
	foreach (HxGameMaster *gm, games->values()) {
		GameBasicInfo info = gm->basicInfo(guest->peerAddress());
		QDataStream out(guest);
		out << info.mapName << info.isProtected << info.isRestricted << info.languageId << info.difficultyLevel;
	}
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
