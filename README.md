anim10.py
=========

Animation library for python 3. It is port of kikito's
[anim8 library](https://github.com/kikito/anim8).

Documentation
=============
I am very sorry, but documentation is not ready yet. You can see
the documentation in the source code of the anim10.py python file.
Also, you can view docs in the anim8
[README.md](https://github.com/kikito/anim8/blob/master/README.md).

Example
=======
Read two example files:
* 1945-demo.py
* witch-demo.py

#### In two lines

First of all, you need to derive from the Frame class:
```
class PyGameFrame(Frame):
    def create_frame(self, width, height):
        return pygame.Surface((width, height))

    def draw(self, canvas, image, x, y):
        rect = (self.x, self.y, self.width, self.height)
        self.quad.blit(image, (0, 0), rect)

        canvas.blit(self.quad, (x, y))
```

And now you can use:
```
from anim10 import new_animation, new_grid

image = pygame.image.load('media/witch.png')

grid = new_grid(PyGameFrame, 32, 32, 384, 256)
animation = new_animation(grid('1-3', 1, 2, 1), 0.15)

animation.draw(screen, image, player_x, player_y)
```
