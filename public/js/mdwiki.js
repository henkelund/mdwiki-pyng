(function (exports, ng) {
    'use strict';

    /**
     * App
     *
     */
    exports.mdwiki = ng.module('mdwiki', ['ngRoute']);

    /**
     * Route provider
     *
     */
    exports.mdwiki.config(['$routeProvider',
        function ($routeProvider)
    {
        $routeProvider.
            when('/:filename*', {
                template: '<div ng-bind-html="contents"></div>',
                controller: 'FileCtrl',
                reloadOnSearch: false
            });
    }]);

    /**
     * File Service Factory
     *
     */
    exports.mdwiki.factory('fileService',
        ['$http', '$q', function ($http, $q)
    {
        var fileService = {

            /**
             * Get file info for given path from backend
             *
             */
            getFile: function (fileName) {
                var promise = $http.get('/file/' + fileName)
                    .then(function (transport) {
                        if (transport.data.errors !== undefined
                                && transport.data.errors.length > 0) {
                            return $q.reject(transport.data.errors);
                        }
                        return transport.data;
                    });
                return promise;
            }

        };
        return fileService;
    }]);

    /**
     * Search Service Factory
     *
     */
    exports.mdwiki.factory('searchService',
        ['$http', function ($http)
    {
        var searchService = {

            search: function (query) {
                var promise = $http.get('/search/' + query)
                    .then(function (transport) {
                        return transport.data;
                    });
                return promise;
            }
        };
        return searchService;
    }]);

    /**
     * File Controller
     *
     */
    exports.mdwiki.controller('FileCtrl',
        ['fileService', '$scope', '$rootScope', '$routeParams', '$sce',
            function (fileService, $scope, $rootScope, $routeParams, $sce)
    {
        fileService.getFile($routeParams.filename).then(function (file) {
            if (file.type == 'file') {
                $scope.contents = $sce.trustAsHtml(file.contents);
                $scope.$$postDigest(function () {
                    $rootScope.$emit('fileOpened', $routeParams.filename);
                });
            }
        }).catch(function (errors) {
            //TODO: pass errors to message controller
            console.log(errors);
        });
    }]);

    /**
     * Tree Controller
     *
     */
    exports.mdwiki.controller('TreeCtrl',
        ['fileService', '$scope', '$rootScope', '$q',
            function (fileService, $scope, $rootScope, $q)
    {
        // Function for loading directory contents
        $scope.open = function (dir, parent) {

            var parentPath = parent === undefined ? '' : parent.path + '/';
            var path = parentPath + dir;
            return fileService.getFile(path).then(function (node) {
                if (node.type == 'dir') {
                    node.path = path;
                    if (parent === undefined) {
                        $scope.root = node;
                    } else {
                        if (parent.subdirs === undefined) {
                            parent.subdirs = {};
                        }
                        parent.subdirs[dir] = node;
                    }
                    node.isOpen = true;
                    return node;
                } else {
                    return $q.reject([path + ' is not a directory']);
                }
            }).catch(function (errors) {
                //TODO: pass errors to message controller
                console.log(errors);
            });
        };

        // Function for recursively opening a path
        $scope.openPath = function (path, parent) {
            if (parent === undefined) {
                parent = $scope.root;
            }
            var segments = path.split('/');
            var segment = segments.shift();
            if (segment == '') {
                return;
            }
            if (parent.subdirs !== undefined
                    && parent.subdirs[segment] !== undefined) {
                parent.subdirs[segment].isOpen = true;
                $scope.openPath(segments.join('/'), parent.subdirs[segment]);
            } else {
                $scope.open(segment, parent).then(function (node) {
                    $scope.openPath(segments.join('/'), node);
                });
            }
        }

        // Function called from tree directive to expand / collapse directories
        $scope.toggleOpen = function (dir, parent) {

            // Check if dir contents are already loaded
            if (parent !== undefined
                    && parent.subdirs !== undefined
                    && parent.subdirs[dir] !== undefined) {
                // Toggle openness
                parent.subdirs[dir].isOpen = !parent.subdirs[dir].isOpen;
            } else {
                // Not yet loaded -> call backend
                $scope.open(dir, parent);
            }
        };

        // Load root directory
        $scope.open('').then(function () {
            // Subscribe to file load event once root dir has opened
            $rootScope.$on('fileOpened', function (evt, filename) {
                $scope.openPath(
                    filename
                        .replace(/(^|\/)[^\/]+$/, '') // trim basename
                        .replace(/^\//, '')           // and leading slash
                );
            });
        });

    }]);

    /**
     * Search Controller
     *
     */
    exports.mdwiki.controller('SearchCtrl',
        ['searchService', '$scope', '$sce',
            function (searchService, $scope, $sce)
    {
        $scope.minQueryLength = 3;
        $scope.nextQuery = false;

        // Search function trying to prevent concurrent service calls
        $scope.serviceSearch = function (query) {
            if ($scope.nextQuery !== false) {
                $scope.nextQuery = query;
                return;
            }
            $scope.nextQuery = query;
            searchService.search(query).then(function (result) {

                for (var i = 0; i < result.hits.length; ++i) {
                    result.hits[i].safeHighlights =
                        $sce.trustAsHtml(result.hits[i].highlights);
                }
                $scope.hits = result.hits;

                var correction = result.correction;
                if (correction !== undefined && correction) {
                    $scope.correction = correction.replace(/<[^>]+>/gm, '');
                    $scope.safeCorrection = $sce.trustAsHtml(correction);
                } else {
                    $scope.correction = false;
                }

            }).catch(function (errors) {
                //TODO: pass errors to message controller
                console.log(errors);
            }).finally(function () {
                var nextQuery = $scope.nextQuery;
                $scope.nextQuery = false;
                if (nextQuery != query) {
                    $scope.serviceSearch(nextQuery);
                }
            });
        };

        // ngChange callback for search input
        $scope.search = function (query) {
            query = query.replace(/(^\s+)|(\s+$)/, '');
            if (query.length >= $scope.minQueryLength) {
                $scope.serviceSearch(query);
            }
        };
    }]);

    /**
     * Table of Contents Controller
     *
     */
    exports.mdwiki.controller('TocCtrl',
        ['$scope', '$rootScope', function ($scope, $rootScope)
    {
        $scope.toc = [];

        $scope.buildToc = function (baseUrl) {
            $scope.toc = [];
            var headings = document.querySelectorAll('[id^="toc_"]');
            for (var i = 0; i < headings.length; ++i) {
                var heading = ng.element(headings[i]);
                var levelMatch = heading.prop('tagName').match(/\d+$/);
                $scope.toc.push({
                    url: baseUrl + '#' + heading.attr('id'),
                    level: levelMatch ? parseInt(levelMatch[0]) : 7,
                    title: heading.text()
                });
            }
        };

        $rootScope.$on('fileOpened', function (evt, filename) {
            $scope.buildToc('#/' + filename);
            $scope.$apply();
        });
    }]);

    /**
     * Tree directive
     *
     */
    exports.mdwiki.directive('tree', ['$compile', function ($compile)
    {
        return {
            restrict    : 'E',
            templateUrl : 'templates/tree.html',
            transclude  : true,
            scope: {
                node         : '=',
                onToggleOpen : '&',
                toggleOpenFn : '='
            },
            compile: function(tElem, tAttr, transclude) {
                var contents = tElem.contents().remove();
                var compiledContents;
                return function (scope, iElem, iAttr) {
                    if (!compiledContents) {
                        compiledContents = $compile(contents, transclude);
                    }
                    compiledContents(scope, function (clone, scope) {
                        iElem.append(clone);
                    });
                }
            }
        };
    }]);

    /**
     * Filter removing .md extension from file names
     *
     */
    exports.mdwiki.filter('stripExtension', function ()
    {
        return function (filename) {
            return filename.replace(/\.md$/i, '');
        };
    });

})(window, angular);

