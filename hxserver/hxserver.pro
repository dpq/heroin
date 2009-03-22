# -------------------------------------------------
# Project created by QtCreator 2009-03-20T21:27:00
# -------------------------------------------------
QT += network script sql
QT -= gui

TARGET = hxserver

CONFIG += console
CONFIG -= app_bundle

TEMPLATE = app
SOURCES += main.cpp \
    hxgatekeeper.cpp \
    hxgamemaster.cpp
HEADERS += hxgatekeeper.h \
    hxgamemaster.h
LIBS += -L/usr/lib/ -loping
