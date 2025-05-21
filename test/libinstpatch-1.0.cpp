#include <libinstpatch/libinstpatch.h>

int main()
{
    guint major, minor, micro;
    ipatch_version(&major, &minor, &micro);

    AEDI_EXPECT(major == IPATCH_VERSION_MAJOR);
    AEDI_EXPECT(minor == IPATCH_VERSION_MINOR);
    AEDI_EXPECT(micro == IPATCH_VERSION_MICRO);

    return 0;
}
