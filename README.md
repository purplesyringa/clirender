# CLI render

`clirender` is a Python library for rendering GUI in command line. This is **not** a library for rendering windows but for rendering full-screen applications.


## Installation

Using pip: `pip install clirender`.

Using git: `git clone https://github.com/imachug/clirender`.


## Usage

`clirender` should usually be used with XML. After a valid clirender-XML document is created, it can be rendered like this:

```python
from clirender.layout import xml_parser, Layout

with open("myapp.xml") as f:
    xml = f.read()

root = xml_parser.fromXml(xml)

layout = Layout(root)
layout.render()
```


## XML format

The syntax is just an XML. The document should not be surrounded by `<?xml` tag. If absolutely necessary, it can be surrounded by `<Container>` and `</Container>`.


## Values

Attributes can be specified for nodes. However, some of them have special meaning.

### Inheritable

Some of attributes are inheritable, i.e. `name="inherit"` will be parsed as *name=the value of this attrubute of parent*. However, your structure may be deep:

```xml
<A>
    <B>
        <C name="asdf"></C>
        <C name="asdf"></C>
    </B>
    <B>
        <C name="asdf"></C>
        <C name="asdf"></C>
    </B>
</A>
```

You may want to specify `asdf` only once:

```xml
<A name="asdf">
    <B name="inherit">
        <C name="inherit"></C>
        <C name="inherit"></C>
    </B>
    <B name="inherit">
        <C name="inherit"></C>
        <C name="inherit"></C>
    </B>
</A>
```

However, `<A>` or `<B>` may not have `name` attribute, or you may want not to apply `name` to them. Then you can use `inherit-name` attribute:

```xml
<A inherit-name="asdf">
    <B inherit-name="inherit">
        <C name="inherit"></C>
        <C name="inherit"></C>
    </B>
    <B inherit-name="inherit">
        <C name="inherit"></C>
        <C name="inherit"></C>
    </B>
</A>
```


### Size

Such attributes as `width` and `height` are parsed using special rules.

When just a number (integer or float) is present, it is interpreted as the count of characters (i.e. columns and rows).

If a percent sign is added at the end, this is parsed as percentage of the parent size. For example, `width="80%"` means `parent_width * 0.8`. If parent size is not defined (i.e. the parent is a container which adjusts its size according to the size of its children), the size of the parent of the parent is checked, and so on.

The keyword `stretch` can be used if the parent is a container adjusting its size, then `stretch` means *the size of container along the main axis*. An example will be given in `<Switch />` section.

Expressions can be used. For example, `stretch * 0.8` means *80% of the size of container along the main axis*.


### Color

Attributes `bg` and `color` (on most figures) are parsed as colors.

`#RRGGBB` or `#RGB` can be used on terminals supporting 24-bit colors. `black`, `yellow`, `red` and a few other names can be used everywhere. For terminals that don't support 24-bit colors, a fallback should be present: `#RRGGBB | name` (e.g. `#FFF | white`).


## Nodes

### Rect

`<Rect />` can be used for rendering rectangles.

Attributes:
1. `width` (required)
2. `height` (required)
3. `bg` (default: *None*)

A rectangle of color `bg`, or a transparent rectangle if `bg` is not present, will be drawn.

Example:
```xml
<Rect width="20" height="10" bg="red" /> <!-- a square on most terminals -->
```


### StackPanel

`<StackPanel>` is a container.

Attributes:
1. `width` (default: *None*)
2. `height` (default: *None*)
3. `bg` (default: *None*)
4. `orientation` (default: `horizontal`)

`orientation` is the main axis.

Example: *Draw a yellow rectangle next to a red rectangle*
```
<StackPanel>
    <Rect width="20" height="10" bg="red" />
    <Rect width="25" height="5" bg="yellow" />
</StackPanel>
```

Example: *Draw a yellow rectangle unders a red rectangle*
```
<StackPanel orientation="vertical">
    <Rect width="20" height="10" bg="red" />
    <Rect width="25" height="5" bg="yellow" />
</StackPanel>
```

Example: *Draw a yellow rectangle next to a red rectangle, both inside a green rectangle. The height is the sum of the height of the children, i.e. 15*
```
<StackPanel width="30" bg="green">
    <Rect width="20" height="10" bg="red" />
    <Rect width="25" height="5" bg="yellow" />
</StackPanel>
```


### Switch

`<Switch />` can be used inside `<StackPanel>` only. After several nodes were rendered along the main axis, `<Switch />` will return to the beginning of the main axis and jump down along the alternate axis.

Example: *Draw red and green rectangles on the first row and blue and yellow rectangles in the second row*
```
<StackPanel orientation="horizontal">
    <Rect width="4" height="2" bg="red" />
    <Rect width="4" height="2" bg="green" />
    <Switch />
    <Rect width="4" height="2" bg="blue" />
    <Rect width="4" height="2" bg="yellow" />
</StackPanel>
```

`<Switch />` will not help you to draw a table if the size of the items is different. For example:
```
<StackPanel orientation="horizontal">
    <Rect width="4" height="3" bg="red" />
    <Rect width="8" height="2" bg="green" />
    <Switch />
    <Rect width="8" height="2" bg="blue" />
    <Rect width="4" height="3" bg="yellow" />
</StackPanel>
```


#### Stretch

`stretch` can be used as width or height on `<StackPanel>` children. This can only be used with `<Switch />` nodes.

Example: *Make E the size of A + B + C + D*
```
    <StackPanel orientation="horizontal">
        <A /><B /><C /><D />
        <Switch />
        <E width="stretch" />
    </StackPanel>
```

`stretch` is the size of the main axis. So, when you need the alternate axis (i.e. make all the items the same width), you can use the following trick:
```
    <StackPanel orientation="horizontal">
        <A width="200" /><Switch />
        <B width="stretch" /><Switch />
        <C width="stretch" /><Switch />
        <D width="stretch" /><Switch />
        <E width="stretch" />
    </StackPanel>
```

Example:
```xml
<StackPanel orientation="horizontal">
    <Rect width="stretch" height="1" bg="blue" />
    <Switch />
    <StackPanel orientation="vertical">
        <Rect width="2" height="stretch" bg="blue" />
        <Switch />
        <Rect width="3" height="2"></Rect>
        <Switch />
        <Rect width="10" height="stretch" bg="blue" />
    </StackPanel>
    <Switch />
    <Rect width="stretch" height="5" bg="blue" />
</StackPanel>
```

### Text

`<Text>` is a text container.

Attributes:
1. width (default: *None*)
2. bg (default: *None*)
3. color (default: *None*)
4. bright (default: *False*)
5. fill (default: *False*)

`<Text>text</Text>` will render `text` in the place where `<Text>` is present. `width` can be set to make `<Text>` occupy more space if necessary. `bg` sets the background of text, including the part added by `width`. `color` sets the foreground color. `bright` makes the text both bright and bold on most terminals.

Finally, if `fill` is *True*, the character given inside `<Text>` will be duplicated `width` times. This is helpful if you don't know the size of the container, e.g. you want to draw a horizontal line:
```xml
<Text width="100%" fill="fill" color="#FFF | white">_</Text>
```

Notice that though `bg` is *None* by default, on most terminals this will mean `black`. So make sure to set the background color correctly or use `bg="inherit"` if possible.


### Container

`<Container>` is somewhat a proxy for nodes. `<Container><Node /></Container>` passes all data to `<Node />`, so it is equal to just `<Node />`. `<Container>` does not work with `inherit-...` attributes - they are inherited automatically.


### AlignRight

`<AlignRight>` is a one-node container. It aligns the child to the right of itself.

Attributes:
1. width (required)
2. height (default: *None*)
3. bg (default: *None*)

Example:
```xml
<AlignRight width="40" bg="red">
    <StackPanel orientation="horizontal" bg="inherit">
        <Rect width="0" height="1" /> <!-- top offset -->
        <Switch />

        <Text bg="inherit" color="yellow">Hello world!</Text>
        <Rect width="2" height="0" /> <!-- right offset -->

        <Switch />
        <Rect width="0" height="1" /> <!-- bottom offset -->
    </StackPanel>
</AlignRight>
```


## Defines

When some code is used several times, one may want to use `include` directive or something like that. `clirender` has *defines* for this case.

The simpliest define looks like this:
```xml
<Container>
    <Define name="Hello">
        <Text color="red" bg="white">Hello!</Text>
    </Define>

    <StackPanel orientation="vertical">
        <Hello />
        <Hello />
    <StackPanel>
</Container>
```

This is equal to:
```xml
<StackPanel orientation="vertical">
    <Text color="red" bg="white">Hello!</Text>
    <Text color="red" bg="white">Hello!</Text>
<StackPanel>
```

Notice that `<Container>` is used in the first case. This is so because XML syntax doesn't accept several nodes at the top. `<Define>` is not a real node, but XML parser doesn't know about this, so `<Container>` is a way to explictly say that.


## Slots

Most parts of code are similar, not equal. So you may want to define some code but a single node. Slots can probably help you.

Let's adjust our `<Hello>` node:
```xml
<Container>
    <Define name="Hello">
        <Slot define="name" />
        <Text color="red" bg="white">Hello, <Slot name="name" />!</Text>
    </Define>

    <StackPanel orientation="vertical">
        <Hello name="world" />
        <Hello name="clirender" />
    <StackPanel>
</Container>
```

`<Slot define="..." />` defines a slot `...`, so later `<DefineName ...=value>` can be used. `<Slot name="..." />` will be replaced with the value of the attribute `...` of `<DefineName />`. This is similar to functions, methods or procedures in modern programming languages.

Slot ` ` (empty string) can also be used:
```xml
<Container>
    <Define name="Hello">
        <Slot define="" /> <!-- Define empty slot -->
        <Text color="red" bg="white">Hello, <Slot />!</Text>
    </Define>

    <StackPanel orientation="vertical">
        <Hello>world</Hello>
        <Hello>clirender</Hello>
    <StackPanel>
</Container>
```

Slot ` ` will also work for nodes, not text:

```xml
<Container>
    <Define name="Hello">
        <Slot define="" />
        <Text color="red" bg="white">Hello, <Slot />!</Text>
    </Define>
    <Define name="Bye">
        <Slot define="" />
        <Text color="green" bg="white">Bye, <Slot />!</Text>
    </Define>

    <Define name="Brackets">
        <Slot define="" />

        <StackPanel orientation="horizontal">
            <Text bg="yellow" color="black">[</Text>
            <Slot />
            <Text bg="yellow" color="black">]</Text>
        </StackPanel>
    </Define>

    <StackPanel orientation="vertical">
        <Brackets><Hello>world</Hello></Brackets>
        <Brackets><Bye>world</Bye></Brackets>
    <StackPanel>
</Container>
```

Slots may also have default values:
```xml
<Container>
    <Define name="Hello">
        <Slot define="" default="world" />
        <Text color="red" bg="white">Hello, <Slot />!</Text>
    </Define>

    <StackPanel orientation="vertical">
        <Hello />
        <Hello>clirender</Hello>
    <StackPanel>
</Container>
```


## Slots inside attributes

Using slots for nodes and text is awesome, but what about e.g. colors?

```xml
<Container>
    <Define name="Hello">
        <Slot define="" default="world" />
        <Slot define="fg" default="red" />
        <Text :color="fg" bg="white">Hello, <Slot />!</Text>
    </Define>

    <StackPanel orientation="vertical">
        <Hello />
        <Hello fg="yellow">clirender</Hello>
    <StackPanel>
</Container>
```

We can define the slot as usual and use `:attr="slot"` structure which will set the value of `attr` to the value of slot `slot`.