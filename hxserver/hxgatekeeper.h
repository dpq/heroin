#ifndef HXGATEKEEPER_H
#define HXGATEKEEPER_H
#include "hxgamemaster.h"

class QScriptEngine;
namespace HxGateKeeperStatic {
	/* Officially unassigned by IANA this port is. Some day, it register even we may. */
	static const quint16 GateKeeperPort = 4048;
	static const quint16 GameMasterMinPort = 49152;
	static const quint16 GameMasterMaxPort = 65535;

	/* Greetings, young Skywalker. I've been expecting you. */
	static const QString Hello = "Heroin Gatekeeper v.0.1/Hello\n";
	/* Boring conversation, anyway. */
	static const QString Begone = "Heroin Gatekeeper v.0.1/Begone\n";
	/* Sorry about the mess. */
	static const QString Error = "Heroin Gatekeeper v.0.1/Pardon\n";

	static const QString GameCreateReport = "Heroin Gatekeeper v.0.1/Create\n";
	static const QString GameJoinReport = "Heroin Gatekeeper v.0.1/Join\n";

	static const QString GameListHeader = "Heroin Gatekeeper v.0.1/Listing\n";
	static const QString GameDetailsHeader = "Heroin Gatekeeper v.0.1/Details\n";
	static const QString GameReplayHeader = "Heroin Gatekeeper v.0.1/Replay\n";

	static const QString GameListRequest = "List";
	static const QString GameDetailsRequest = "Details";
	static const QString GameReplayRequest = "Replay";
	static const QString GameCreateRequest = "Create";
	static const QString GameJoinRequest = "Join";
	static const QString GoodbyeRequest = "Bye";
}

class HxGateKeeper : public QTcpServer {
Q_OBJECT
public:
	HxGateKeeper(QObject *parent = 0);
	~HxGateKeeper();

	quint16 createGame(const GameOptions &options);
	void joinGame(quint16 port);

protected slots:
	void hello();
	void talk();
	void forget();

private:
	void sendGameList(QTcpSocket *guest);
	void sendGameDetails(QTcpSocket *guest, quint32 gameId);
	void sendGameReplay(QTcpSocket *guest, quint32 gameId);
	void farewell(QTcpSocket *guest);
	void pardon(QTcpSocket *guest, QString message);
	QList<QTcpSocket*> *guests;
	QHash<quint16, HxGameMaster*> *games;
	QScriptEngine *jsEngine;

	QList<quint16> *reclaimedPorts;
	quint16 nextFreePort;
	quint32 nextGameId;
};

#endif // HXGATEKEEPER_H
