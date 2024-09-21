# core/feature_registry.py

class FeatureRegistry:
    _features = {}

    @classmethod
    def register(cls, name, dependencies=None):
        def decorator(feature_class):
            cls._features[name] = {
                'class': feature_class,
                'dependencies': dependencies or []
            }
            return feature_class
        return decorator

    @classmethod
    def get_feature(cls, name):
        return cls._features.get(name, {}).get('class')

    @classmethod
    def is_feature_enabled(cls, feature_name):
        return feature_name in cls._features

    @classmethod
    def get_all_features(cls):
        return list(cls._features.keys())

    @classmethod
    def get_feature_dependencies(cls, feature_name):
        return cls._features.get(feature_name, {}).get('dependencies', [])

    @classmethod
    def get_dependent_features(cls, feature_name):
        return [f for f, info in cls._features.items() if feature_name in info['dependencies']]