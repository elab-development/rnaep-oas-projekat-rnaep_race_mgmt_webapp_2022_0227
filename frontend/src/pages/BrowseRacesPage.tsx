import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Input";
import { RaceFetchError } from "@/components/races/RaceFetchError";
import { RaceListSkeleton } from "@/components/ui/Skeleton";
import { useRaces } from "@/features/races/hooks";
import { RaceStatus, type Race } from "@/types/race";
import { formatRaceDate, parseBackendDate } from "@/utils/dates";
import { getErrorMessage } from "@/utils/errors";

const PAGE_SIZE = 9;

function filterRaces(races: Race[], search: string, status: string, location: string) {
  return races.filter((race) => {
    const matchesSearch =
      !search ||
      race.name.toLowerCase().includes(search.toLowerCase()) ||
      race.location.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = !status || race.status === status;
    const matchesLocation =
      !location || race.location.toLowerCase().includes(location.toLowerCase());
    return matchesSearch && matchesStatus && matchesLocation;
  });
}

export function BrowseRacesPage() {
  const { data, isLoading, error, refetch, isFetching } = useRaces();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [location, setLocation] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (error) {
      toast.error(getErrorMessage(error, "Failed to load races."));
    }
  }, [error]);

  const filtered = useMemo(
    () => filterRaces(data ?? [], search, status, location),
    [data, search, status, location],
  );

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const paginated = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  if (error) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
        <div className="mb-8">
          <h1 className="font-display text-4xl font-black text-slate-900">Browse Races</h1>
        </div>
        <RaceFetchError
          error={error}
          onRetry={() => void refetch()}
          isRetrying={isFetching}
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
      <div className="mb-8">
        <h1 className="font-display text-4xl font-black text-slate-900">Browse Races</h1>
        <p className="mt-2 text-slate-600">
          Discover upcoming obstacle course races and secure your spot.
        </p>
      </div>

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <Input
          label="Search"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          placeholder="Name or location"
        />
        <label className="text-sm font-semibold">
          Status
          <select
            className="mt-1.5 w-full rounded-lg border-2 border-slate-300 px-3 py-2.5"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All</option>
            <option value={RaceStatus.UPCOMING}>Upcoming</option>
            <option value={RaceStatus.COMPLETED}>Completed</option>
            <option value={RaceStatus.CANCELLED}>Cancelled</option>
          </select>
        </label>
        <Input
          label="Location"
          value={location}
          onChange={(e) => {
            setLocation(e.target.value);
            setPage(1);
          }}
          placeholder="Filter by city"
        />
      </div>

      {isLoading ? <RaceListSkeleton /> : null}
      {!isLoading && filtered.length === 0 ? (
        <EmptyState
          title="No races currently available."
          description="Check back later for new events."
        />
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {paginated.map((race) => {
          const deadline = parseBackendDate(race.deadline);
          return (
            <article key={race.id} className="rounded-2xl border-2 border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-2">
                <h2 className="font-display text-xl font-bold">{race.name}</h2>
                <Badge label={race.status} tone={race.status} />
              </div>
              <p className="mt-2 text-sm text-slate-600">{race.location}</p>
              <p className="mt-1 text-sm font-semibold">{formatRaceDate(race.date_time)}</p>
              <p className="mt-3 text-lg font-black text-brand">${race.price.toFixed(2)}</p>
              <p className="mt-1 text-xs text-slate-500">Up to {race.max_participants} spots</p>
              {deadline ? (
                <p className="mt-1 text-xs text-slate-500">
                  Registration closes {formatRaceDate(race.deadline)}
                </p>
              ) : null}
              <Link
                to={`/races/${race.id}`}
                className="mt-4 inline-block text-sm font-bold text-brand hover:underline"
              >
                View details →
              </Link>
            </article>
          );
        })}
      </div>

      {!isLoading && filtered.length > PAGE_SIZE ? (
        <div className="mt-8 flex items-center justify-center gap-3">
          <Button
            variant="secondary"
            disabled={currentPage <= 1}
            onClick={() => setPage((value) => Math.max(1, value - 1))}
          >
            Previous
          </Button>
          <span className="text-sm font-semibold text-slate-600">
            Page {currentPage} of {totalPages}
          </span>
          <Button
            variant="secondary"
            disabled={currentPage >= totalPages}
            onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
          >
            Next
          </Button>
        </div>
      ) : null}
    </div>
  );
}
