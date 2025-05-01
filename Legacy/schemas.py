def package_to_dict(pkg):
    return {
        "id": pkg.id,
        "code": pkg.code,
        "pickup_code": pkg.pickup_code,
        "status": pkg.status,
        "in_time": pkg.in_time.isoformat(timespec="seconds"),
        "out_time": pkg.out_time.isoformat(timespec="seconds") if pkg.out_time else None,
    }