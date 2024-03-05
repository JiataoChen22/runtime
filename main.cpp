#include <iostream>
#include <spdlog/spdlog.h>
#include "src/test/Player.h"
#include "src/runtime/ClassFactory.h"

int main() {
    std::cout << "Hello, World!" << std::endl;

    auto player = runtime::ClassFactory::fromClass("Player");

    player->setField("mId", 2);

    spdlog::info("mId: {}", player->getField<int>("mId"));

    delete player;

    return 0;
}
