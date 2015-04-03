import QtQuick 2.4
import QtQuick.Controls 1.3
import QtQuick.Layouts 1.1

Item {
    width: 640
    height: 480

    property alias button3: button3
    property alias button2: button2
    property alias button1: button1

    RowLayout {
        anchors.centerIn: parent
    }

    Text {
        id: text1
        x: 121
        y: 173
        width: 293
        height: 14
        text: qsTr("Text")
        font.pixelSize: 12
    }
}
