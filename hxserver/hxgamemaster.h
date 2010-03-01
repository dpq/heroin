#ifndef HXGAMEMASTER_H
#define HXGAMEMASTER_H
#include <QString>
#include <QPair>
#include <QHostAddress>
#include <QTcpServer>
#include <QSslSocket>
#include <QPoint>

enum GameState { OpenState, RunningState, FinishedState };
enum SlotType { Closed = 0, Human = 1, AI = 2 };
enum RestrictionFlag { Password = 1, Subnet = 2, Ping = 4, Lang = 8 };
enum PlayerColor { Red = 1, Blue, Green, Tan, Purple, Orange };
enum DifficultyLevel { Pawn, Knight, Rook, Queen, King };

// TODO random maps?

struct GameOptions {
	QString mapName;
	QString passwordRestriction;
	QPair<QHostAddress, quint16> subnetRestriction;
	qint32 pingRestriction;
	quint8 languageId;
	DifficultyLevel difficultyLevel;
};

struct GameBasicInfo {
	quint32 gameId;
	quint8 gameState;
	quint8 availableSlots; /* unoccupied human slots */
	QString mapName;
	bool isProtected;  /* by password */
	bool isRestricted; /* by network settings */
	quint8 languageId;
	DifficultyLevel difficultyLevel;
};

struct GameDetailedInfo {
	QHash<PlayerColor, QString> players;
	QPoint mapSize;
	QPixmap preview;
};

class HxGameMaster : public QTcpServer {
Q_OBJECT
public:
	HxGameMaster(quint32 gameId, GameOptions options);
	virtual QSslSocket *nextPendingConnection();
	GameBasicInfo basicInfo(QHostAddress guestHost);
	GameDetailedInfo detailedInfo();

private:
	void incomingConnection(int socketDescriptor);
	GameOptions options;
	quint32 gameId;
	quint8 gameState;
};

#endif // HXGAMEMASTER_H
