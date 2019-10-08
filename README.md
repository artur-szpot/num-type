# num-type
A Python typing game focused around the numeric keypad written in pygame.

## Prerequisites
To run the game, a Python 3 interpreter and the [pygame](https://www.pygame.org/news) module will have to be installed.

pygame is easy to install with pip, as evidenced by its [installation wiki page](https://www.pygame.org/wiki/GettingStarted).

## How to play
Currently, the game only features one mode of play, in which the objective is to destroy blocks by typing in their codes with the numeric keyboard before time runs out.

After typing a number, press enter to attempt destroying a block - if one with the typed number exists, it will be destroyed. This awards points and spawns a new, tougher block in its place. Collecting a total of 10.000 points equals victory.

If a mistake is made and the block does not exist, one heart will be lost. At the start of the game, the player has 10 hearts. Losing all hearts equals defeat.

If a block's lifespan runs out before it is destroyed, it will destroy itself, which causes points to be lost and a new, tougher block to be spawned in its place. Going below 0 in points equals defeat.

It is possible to make corrections to the typed-in numbers by pressing backspace to erase the last digit or pressing escape to clean the input completely. Be careful, however - pressing escape when the input is empty will equal surrender, and trigger defeat.

## Contributions

Any comments, bug reports, mode ideas or development cooperation offers are welcome.

## Built with

IDLE alone

## Author

**Artur Szpot** ([GitHub](https://github.com/artur-szpot)) - so far, everything

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details