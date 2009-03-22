#include "hxgamemaster.h"
#include <oping.h>

HxGameMaster::HxGameMaster(quint32 gameId, GameOptions options) : QTcpServer() {
    this->options = options;
}

QSslSocket *HxGameMaster::nextPendingConnection() {
    return 0;
}

void HxGameMaster::incomingConnection(int socketDescriptor) {
}

GameDetailedInfo HxGameMaster::detailedInfo() {

}

GameBasicInfo HxGameMaster::basicInfo(QHostAddress guestHost) {
    GameBasicInfo i;
    i.gameId = gameId;
    i.mapName = options.mapName;
    i.languageId = options.languageId;
    i.difficultyLevel = options.difficultyLevel;
    i.isProtected = (options.password != "");
    bool pingAllowed = true, subnetAllowed = true;
    // TODO check for errors here
    if (options.pingRestriction != 0) {
	pingobj_t *pingObj = ping_construct();
	ping_host_add(pingObj, guestHost.toString().toAscii());
	int pingTime = ping_send(pingObj);
	ping_destroy(pingObj);
	if (pingTime <= 0 || pingTime > options.pingRestriction)
	    pingAllowed = false;
    }
    if (options.subnetRestriction != QPair<QHostAddress, quint16>())
	subnetAllowed = guestHost.isInSubnet(options.subnetRestriction.first, options.subnetRestriction.second);
    i.isAvailable = pingAllowed && subnetAllowed;
    // TODO
    i.totalSlots = 0;
    i.availableSlots = 0;
    return i;
}
