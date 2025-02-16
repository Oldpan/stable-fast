import dataclasses
import torch
import sfast


def tree_copy_(dest, src):
    if isinstance(dest, torch.Tensor):
        dest.copy_(src)
    elif isinstance(dest, (list, tuple)):
        assert len(dest) == len(src)
        for x, y in zip(dest, src):
            tree_copy_(x, y)
    elif dataclasses.is_dataclass(dest):
        assert len(dest) == len(src)
        for field in dataclasses.fields(dest):
            tree_copy_(getattr(dest, field.name), getattr(src, field.name))
    elif isinstance(dest, dict):
        assert len(dest) == len(src)
        for k in dest:
            tree_copy_(dest[k], src[k])
    else:
        assert type(dest) == type(src)


def tree_copy(src):
    if isinstance(src, torch.Tensor):
        return src.clone()
    elif isinstance(src, (list, tuple)):
        return type(src)(tree_copy(x) for x in src)
    elif dataclasses.is_dataclass(src):
        return type(src)(**{
            field.name: tree_copy(getattr(src, field.name))
            for field in dataclasses.fields(src)
        })
    elif isinstance(src, dict):
        return type(src)((k, tree_copy(v)) for k, v in src.items())
    else:
        return src


def shadow_copy(obj):
    if isinstance(obj, torch.Tensor):
        return sfast._C._create_shadow_tensor(
            obj) if obj.device.type == 'cuda' else obj
    elif isinstance(obj, (list, tuple)):
        return type(obj)(shadow_copy(x) for x in obj)
    elif dataclasses.is_dataclass(obj):
        return type(obj)(**{
            field.name: shadow_copy(getattr(obj, field.name))
            for field in dataclasses.fields(obj)
        })
    elif isinstance(obj, dict):
        return type(obj)((k, shadow_copy(v)) for k, v in obj.items())
    else:
        return obj
