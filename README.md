# podplay-api

[![GitHub Release][releases-shield]][releases]
[![Python Versions][py-versions-shield]][py-versions]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE.md)

[![Build Status][build-shield]][build]
[![Code coverage][codecov-shield]][codecov]


Asynchronous Python client for the PodPlay.com API

## Installation

```bash
pip install podplay-api
```

## Usage

The following are some basic examples of how to use the library.

Get information about a specific podcast:

```python
import asyncio

from podplay_api import PodPlayClient


async def main():
    """Main function."""
    async with PodPlayClient() as client:
        podcast = await client.get_podcast(podcast_id=31428)
        print(podcast)


if __name__ == "__main__":
    asyncio.run(main())
```

Get all episodes for a specific podcast:

```python
episodes = await client.get_podcast_episodes(podcast_id=31428)
for episode in episodes:
    print(episode)
```

Search for a specific podcast:

```python
search_results = await client.search_podcast("dude")
for podcast in search_results:
    print(podcast)
```

Get top podcasts of a category:

```python
podcasts = await client.get_podcasts_by_category(31428)
for podcast in podcasts:
    print(podcast)
```


## Contributing

If you'd like to contribute to the project, please submit a pull request or open an issue on the GitHub repository.

## License

podplay-api is licensed under the MIT license. See the LICENSE file for more details.

## Contact

If you have any questions or need assistance with the library, you can contact the project maintainer at @bendikrb.

[license-shield]: https://img.shields.io/github/license/bendikrb/podplay_api.svg
[license]: https://github.com/bendikrb/podplay_api/blob/main/LICENSE
[releases-shield]: https://img.shields.io/pypi/v/podplay-api
[releases]: https://github.com/bendikrb/podplay_api/releases
[build-shield]: https://github.com/bendikrb/podplay_api/actions/workflows/tests.yaml/badge.svg
[build]: https://github.com/bendikrb/podplay_api/actions/workflows/tests.yaml
[maintenance-shield]: https://img.shields.io/maintenance/yes/2024.svg
[py-versions-shield]: https://img.shields.io/pypi/pyversions/podplay-api
[py-versions]: https://pypi.org/project/podplay-api/
[codecov-shield]: https://codecov.io/gh/bendikrb/podplay_api/graph/badge.svg?token=011O5N9MKL
[codecov]: https://codecov.io/gh/bendikrb/podplay_api
