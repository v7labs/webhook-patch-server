# WEBHOOK PATCH SERVER

This code is provided as an "as-is" project that exemplifies the usage of [V7-workflows](https://docs.v7labs.com/v2.0/docs/use-workflow-to-manage-your-projects) and more specifically [V7-webhooks.](https://docs.v7labs.com/v2.0/docs/the-webhook-stage). 


The project provides code to start a [FLASK-server](https://flask.palletsprojects.com/en/2.2.x/) hosting a REST web-api that allows the generation of patches from a larger image based on annotations generated on the V7 platform. The current version does **only support** `images` and not 3D-volumes, videos or other data formats.

![alt text](/illustrations/image_patch_illustrations.png)

## Annotation format

The basic functionallity of the server is to crop out patches from larger images and upload them to a new dataset, this can be done by generating `bounding box` annotations on the V7 platform and having the word `patch` in the name of the annotation. This also means that any annotations without the keyword `patch` will be ignored. Further, it is possible to generate multiple patches from a single bounding box by adding the following formating in the annotation name `(NxM)` were N and M is the number of rows and columns that should be extracted from the bounding box.

This is very useful for quickly cropping up a large image into multiple patches since you can just mark the whole image (or part of it) with a bounding box called `patch (4x6)` for example, and then have those 26 equally sized patches added to your target dataset. It is also easy to copy-and-past this annotaion to all relevant images in your dataset when annotate if you want to apply the exact same patch transfomration on all images.


## Endpoints

| Endpoint | Method  | Description                                                 | Query |
| -------- | ------- | ----------------------------------------------------------- | ------
| /        | GET     | A test enpoint that can be used to test server connection   | - |
| /webhook | POST    | Crops an image based on passed annotations and saves the new patches to a new dataset defined by the target query   | target |


## Install

To install this project, clone it from the project github via
```
git clone URL
```

## Starting the server

To simplyfi the usage it is highly recommended to have docker and make installed in your system. To build the server just run the following command in your CMD/terminal.

```
make build
```

Before we can start the server, you need to generate an API-key using the frontend of V7-darwin and export it as an enviornment variable (so that the server can access images and datasets), for linux write

```
export V7_KEY="your_api_key"
```

and for windows type


```
set V7_KEY="your_api_key"
```

Once the API key is in place, start the server by typing

```
make run_server
```

This should give the following output on your terminal indicating that the server is up and running:


![alt text](/illustrations/running_server_example.png)

To close the server, use `ctrl+c`.

## V7 workflow

For more details about setting up the V7 workflow associated with this use-case please see the [following documentation]. Here it is described how to configurate and use the webhook to communicate with the running server.


