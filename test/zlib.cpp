#include <string.h>
#include <zlib.h>

int main()
{
    z_stream stream = {};

    AEDI_EXPECT(deflateInit(&stream, Z_DEFAULT_COMPRESSION) == Z_OK);

    constexpr size_t BUFFER_SIZE = 1024;
    unsigned char reference[BUFFER_SIZE];

    for (size_t i = 0; i < BUFFER_SIZE; ++i)
    {
        reference[i] = static_cast<unsigned char>(i % 47);
    }

    unsigned char deflated[BUFFER_SIZE] = {};

    stream.next_in = reference;
    stream.avail_in = BUFFER_SIZE;
    stream.next_out = deflated;
    stream.avail_out = BUFFER_SIZE;

    AEDI_EXPECT(deflate(&stream, Z_FINISH) == Z_STREAM_END);
    AEDI_EXPECT(deflateEnd(&stream) == Z_OK);

    stream = {};

    AEDI_EXPECT(inflateInit(&stream) == Z_OK);

    unsigned char inflated[BUFFER_SIZE] = {};

    stream.next_in = deflated;
    stream.avail_in = BUFFER_SIZE;
    stream.next_out = inflated;
    stream.avail_out = BUFFER_SIZE;

    AEDI_EXPECT(inflate(&stream, Z_FINISH) == Z_STREAM_END);
    AEDI_EXPECT(inflateEnd(&stream) == Z_OK);

    AEDI_EXPECT(memcmp(reference, inflated, BUFFER_SIZE) == 0);

    return 0;
}
