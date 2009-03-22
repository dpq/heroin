#ifndef HXGAMEMASTER_H
#define HXGAMEMASTER_H
#include <QString>
#include <QPair>
#include <QHostAddress>
#include <QTcpServer>
#include <QSslSocket>
#include <QPoint>

enum GameState { Open, Running, Finished };
enum SlotType { Human = 1, Computer = 2 };
enum RestrictionFlag { Password = 1, Subnet = 2, Ping = 4 };
enum PlayerColor { Red = 1, Blue, Green, Tan, Purple, Orange };

struct GameOptions {
    QString mapName;
    QString password;
    QPair<QHostAddress, quint16> subnetRestriction;
    qint32 pingRestriction;
    quint8 languageId;
    quint8 difficultyLevel;
};

struct GameBasicInfo {
    quint32 gameId;
    QString mapName;
    bool isProtected;
    bool isAvailable;
    quint8 languageId;
    quint8 difficultyLevel;
    quint8 totalSlots;
    quint8 availableSlots;
};

struct GameDetailedInfo {
    QHash<PlayerColor, QString> players;
    QPoint mapSize;
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
};

#endif // HXGAMEMASTER_H
