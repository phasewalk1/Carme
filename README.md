
# Carme
This is the working repository for ***Carme***, a *hybrid recommendation* system for users on the ***SB*** platform. 

## Overview
***Carme*** is made possible by the excellent open-source contributions made by [Michael Bizimis](https://github.com/michaelbzms) in his MSc thesis project, [DeepRecommendation](https://github.com/michaelbzms/DeepRecommendation). His thesis outlines the development, implementation and evaluation of three classes of *deep hybrid models*. Checkout the [README](https://github.com/michaelbzms/DeepRecommendation/tree/master/README.md) for more information.


> ***Carme*** forks [DeepRecommendation](https://github.com/michaelbzms/DeepRecommendation) and maintains a vendored version of it ([hybrid](https://github.com/phasewalk1/tree/master/vendored/hybrid)) for use in the ***Carme*** system.
> ***Carme*** uses *AttentionNCF* as described in the *README*.


The ***Carme*** system is largely structured on the original ***DeepRecommendation*** code, and makes the necessary modifications to it to allow for integration with our application (this is why we maintain a *vendored* fork). This includes custom *content providers* for one hot encodings and dynamic profiling. It also likely includes removing code that was only relevant for the thesis experiments.

> This vendored fork can be found in [vendored](https://github.com/phasewalk1/carme/tree/master/vendored/).

Most work done in this repository is done within the vendored fork ([hybrid](https://github.com/phasewalk1/carme/tree/master/vendored/hybrid)). However, we may want to consider using the root repository for preprocessing logic and analysis (the current *DeepRecommendation* code constructs the dataset files using two jupyter notebooks; we will want to extract this functionality into their own files and modify them to work with our data).

## Acknowledgements

 - [DeepRecommendation](https://github.com/michaelbzms/DeepRecommendation)