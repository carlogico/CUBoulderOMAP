# CU Boulder Map ![map status: ](https://github.com/carlogico/CUBoulderOMAP/actions/workflows/main.yml/badge.svg?event=push)

This repo contains a map for CU Boulder.

## Cloning

Clone the repo normally and put the relevant templates in a `Templates` folder within the repo. These files will not be tracked (even using `git-lfs` it would go above GitHub's repo limits...). Use [OpenOrienteeringMapper](https://github.com/OpenOrienteering/mapper) to edit the map.

Make sure to create a symbolic link form the [pre-commit file](.githooks/pre-commit) and make it executable, eg:

```console
➜ cd .git/hooks

➜ ln -s ../../.githooks/pre-commit

➜ chmod -x pre-commit

➜ cd ../..

```

## Contributing

Before you make any changes:
* create a new [map part](https://www.openorienteering.org/mapper-manual/pages/map_parts.html) using the `Map > Add new part...` menu item and give it a distinguishable name
* switch to the newly created map part using the [map toolbar](https://www.openorienteering.org/mapper-manual/pages/toolbars.html#map-parts-toolbar)
* commit as usual

> [!CAUTION]
> If the `pre-commit` hook is set up properly, committing will clean the Template paths (this shouldn't affect using the map) and more importantly wipe your undo/redo history!! Make sure you reload the map after committing.